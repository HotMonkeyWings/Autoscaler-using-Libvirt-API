#!/usr/bin/python
import sys
import libvirt

conn = None
try:
    # This opens a connection with read-write access
    conn = libvirt.open("qemu:///system")

    # This opens a connection with read-only access
    #conn = libvirt.openReadOnly("qemu:///system")

except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)
conn.close()
exit(0)
