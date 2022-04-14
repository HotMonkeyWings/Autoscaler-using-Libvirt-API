# Connecting to a remote QEMU hypervisor
#!/usr/bin/python

import sys
import libvirt

conn = None
try:
    conn = libvirt.open('qemu+tls://host2/system')
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)
conn.close()
exit(0)
