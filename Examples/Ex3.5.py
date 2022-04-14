# Connecting to a local QEMU hypervisor
#!/usr/bin/python

import sys
import libvirt

conn = None
try:
    conn = libvirt.open('qemu:///system')
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)
conn.close()
exit(0)
