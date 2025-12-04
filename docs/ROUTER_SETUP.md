# Router Setup Guide

## Juniper vSRX Image

VRHost Lab currently supports Juniper vSRX routers. You'll need to provide your own vSRX image.

### Download vSRX Image

1. **Register for Juniper account:**
   - Go to https://www.juniper.net
   - Create a free account

2. **Download vSRX KVM image:**
   - Navigate to Software Downloads
   - Search for "vSRX"
   - Download the KVM/QEMU image (recommended: vSRX 23.2R2 or later)
   - File will be named similar to: `junos-media-vsrx-x86-64-vmdisk-23.2R2.21.qcow2`

3. **Place the image:**
```bash
   sudo cp junos-media-vsrx-*.qcow2 /var/lib/libvirt/images/vsrx.qcow2
```

4. **Verify:**
```bash
   ls -lh /var/lib/libvirt/images/vsrx.qcow2
   # Should show the file
```

### mkjuniper Script

The `mkjuniper` script is automatically installed to `/usr/local/bin/mkjuniper` during installation.

**Usage:**
```bash
mkjuniper <name> <ip> <type> <ram_gb> <vcpus>

# Example:
mkjuniper r1 10.10.50.10 vsrx 4 2
```

**What it does:**
- Creates a new vSRX VM using the base image
- Configures networking
- Allocates specified resources
- Starts the router (takes ~90 seconds to boot)

### Requirements

**Minimum per router:**
- 2GB RAM
- 1 vCPU
- 10GB disk

**Recommended per router:**
- 4GB RAM
- 2 vCPUs
- 20GB disk

### Troubleshooting

**Router won't start:**
```bash
# Check if base image exists
ls -lh /var/lib/libvirt/images/vsrx.qcow2

# Check libvirt logs
sudo journalctl -u libvirtd -n 50
```

**Router not accessible:**
- Wait 90-120 seconds for boot
- Check router console: `virsh console <router-name>`
- Verify network: `ip addr` on router

### Future Platform Support

Support for additional router platforms is planned:
- Cisco CSR1000v
- Arista vEOS
- Cisco IOSv/IOSvL2

**Community contributions welcome!** If you'd like to add support for another platform, please submit a PR.
