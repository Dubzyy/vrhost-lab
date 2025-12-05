import subprocess
import secrets
import time
from typing import Dict, Optional

class ConsoleService:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.base_port = 7681
        self.next_port = self.base_port
        self.session_timeout = 600  # 10 min

    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired_tokens = []

        for token, session in self.sessions.items():
            if current_time - session['created_at'] > self.session_timeout:
                expired_tokens.append(token)

        for token in expired_tokens:
            self.close_session(token)

    def _find_existing_session(self, router_name: str) -> Optional[str]:
        """Find if there's already a session for this router"""
        for token, session in self.sessions.items():
            if session['router_name'] == router_name:
                return token
        return None

    def _kill_existing_ttyd(self, router_name: str):
        """Kill any existing ttyd and virsh console processes for this router"""
        try:
            # Kill processes for base name
            subprocess.run(
                ['pkill', '-9', '-f', f'ttyd.*virsh console {router_name}'],
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            
            subprocess.run(
                ['pkill', '-9', '-f', f'virsh console {router_name}'],
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            
            # Also kill processes for -re variant (vQFX)
            subprocess.run(
                ['pkill', '-9', '-f', f'ttyd.*virsh console {router_name}-re'],
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            
            subprocess.run(
                ['pkill', '-9', '-f', f'virsh console {router_name}-re'],
                stderr=subprocess.DEVNULL,
                timeout=2
            )

            # Give processes time to die
            time.sleep(0.5)

        except Exception:
            pass

    def create_session(self, router_name: str) -> dict:
        """Create a new console session"""
        self._cleanup_expired_sessions()

        # Check if session already exists for this router
        existing_token = self._find_existing_session(router_name)
        if existing_token:
            # Close the existing session first
            self.close_session(existing_token)

        # Kill any lingering ttyd processes for this router
        self._kill_existing_ttyd(router_name)

        # For vQFX switches, connect to the RE (Routing Engine)
        # Check if this is a vQFX by looking for {name}-re domain
        actual_domain = router_name
        try:
            import libvirt
            conn = libvirt.open('qemu:///system')
            try:
                # Try to find domain with -re suffix (vQFX)
                conn.lookupByName(f"{router_name}-re")
                actual_domain = f"{router_name}-re"
            except libvirt.libvirtError:
                # Not a vQFX, use regular name
                pass
            finally:
                conn.close()
        except Exception:
            pass

        # Generate new session
        token = secrets.token_urlsafe(16)
        port = self.next_port
        self.next_port += 1

        # Start ttyd process
        try:
            process = subprocess.Popen([
                'ttyd',
                '-p', str(port),
                '-i', '0.0.0.0',
                '-t', 'fontSize=14',
                '-t', 'theme={"background": "#1e293b", "foreground": "#e5e7eb"}',
                'virsh', 'console', actual_domain
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Store session info
            self.sessions[token] = {
                'router_name': router_name,
                'port': port,
                'process': process,
                'created_at': time.time()
            }

            return {
                'token': token,
                'port': port,
                'router_name': router_name
            }
        except Exception as e:
            raise Exception(f"Failed to start console session: {str(e)}")

    def get_session(self, token: str) -> Optional[dict]:
        """Get session info by token"""
        self._cleanup_expired_sessions()

        session = self.sessions.get(token)
        if not session:
            return None

        return {
            'token': token,
            'router_name': session['router_name'],
            'port': session['port'],
            'age': int(time.time() - session['created_at'])
        }

    def close_session(self, token: str) -> bool:
        """Close a console session"""
        session = self.sessions.get(token)
        if not session:
            return False

        try:
            # Get router name before removing session
            router_name = session['router_name']

            # Terminate ttyd process
            try:
                session['process'].terminate()
                session['process'].wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                session['process'].kill()
                session['process'].wait(timeout=1)
            except Exception:
                pass

            # Kill any remaining processes for this router
            self._kill_existing_ttyd(router_name)

        except Exception:
            pass

        # Remove from sessions
        del self.sessions[token]
        return True

    def close_all_sessions(self):
        """Close all active sessions"""
        tokens = list(self.sessions.keys())
        for token in tokens:
            self.close_session(token)
