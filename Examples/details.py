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

host = conn.getHostname()
print('Hostname:' + host)
vcpus = conn.getMaxVcpus(None)
print('Maximum support virtual CPUs: ' + str(vcpus))

nodeinfo = conn.getInfo()

print('Model: '+str(nodeinfo[0]))
print('Memory size: '+str(nodeinfo[1])+'MB')
print('Number of CPUs: '+str(nodeinfo[2]))
print('MHz of CPUs: '+str(nodeinfo[3]))
print('Number of NUMA nodes: '+str(nodeinfo[4]))
print('Number of CPU sockets: '+str(nodeinfo[5]))
print('Number of CPU cores per socket: '+str(nodeinfo[6]))
print('Number of CPU threads per core: '+str(nodeinfo[7]))

print('Virtualization type: ' + conn.getType())

conn.close()
exit(0)
