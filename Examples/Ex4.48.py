import sys
import libvirt
from xml.dom import minidom


conn = None
try:
    conn = libvirt.open("qemu:///system")
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)

dom = conn.lookupByName('ubuntu')
ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)

print("The interface IP addresses:")
for (name, val) in ifaces.items():
    if name == 'lo':
        continue
    print(val['addrs'][0]['addr'])

conn.close()
exit(0)
