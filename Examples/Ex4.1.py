#!/usr/bin/python

import sys
import libvirt

conn = None
try:
    conn = libvirt.open('qemu:///system')
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)

domainID = 2
dom = conn.lookupByID(domainID)
if dom == None:
    print('Failed to get the domain object', file=sys.stderr)

conn.close()
exit(0)
