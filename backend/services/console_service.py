import subprocess
import secrets
import time
from typing import Dict, Optional

class ConsoleService:
    def __init__(self):
        self.active_sessions: Dict[str, dict] = {}
        self.session_timeout = 3600  # 1 hour
        self.base_port = 7681  # Starting port for ttyd sessions
        self.next_port = self.base_port
    
    def create_console_session(self, router_name: str, host: str = "0.0.0.0") -> dict:
        """Create a web console session for a router"""
        # Generate secure token
        token = secrets.token_urlsafe(16)
        port = self._get_next_port()
        
        # Start ttyd session
        cmd = [
            'ttyd',
            '-p', str(port),
            '-i', host,  # Listen on all interfaces
            '-t', 'fontSize=14',
            '-t', 'fontFamily="Courier New, monospace"',
            'virsh', 'console', router_name
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Give ttyd time to start
        time.sleep(0.5)
        
        # Store session info
        self.active_sessions[token] = {
            'router_name': router_name,
            'port': port,
            'process': process,
            'created_at': time.time()
        }
        
        return {
            'token': token,
            'port': port
        }
    
    def get_session(self, token: str) -> Optional[dict]:
        """Get console session by token"""
        session = self.active_sessions.get(token)
        if not session:
            return None
        
        # Check if session expired
        if time.time() - session['created_at'] > self.session_timeout:
            self.close_session(token)
            return None
        
        return session
    
    def close_session(self, token: str):
        """Close a console session"""
        session = self.active_sessions.get(token)
        if session:
            try:
                session['process'].terminate()
                session['process'].wait(timeout=5)
            except:
                try:
                    session['process'].kill()
                except:
                    pass
            
            del self.active_sessions[token]
    
    def cleanup_old_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired = [
            token for token, session in self.active_sessions.items()
            if current_time - session['created_at'] > self.session_timeout
        ]
        
        for token in expired:
            self.close_session(token)
    
    def _get_next_port(self) -> int:
        """Get next available port"""
        port = self.next_port
        self.next_port += 1
        return port
