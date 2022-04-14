# Using getCapabilities
#!/usr/bin/python

import sys
import libvirt

conn = None
try:
    conn = libvirt.open('qemu:///system')
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)

caps = conn.getCapabilities()
print('Capabilities:\n' + caps)
conn.close()
exit(0)
