# TODO:
# 1. Spawn VMs
# 2. Report CPU Usage
# 3. Algorithm to spawn new VM
import libvirt
import time

def spawnVM():
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    inactiveDoms = conn.listAllDomains(libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_INACTIVE)
    inactiveDoms.sort(key=lambda dom: dom.name())

    if not inactiveDoms:
        print("No more VMs available!")
        return

    inactiveDoms[0].create()
    print("New VM:", inactiveDoms[0].name(), "has been started.")
    conn.close()

def reportCPUUsage():
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)
    doms = conn.listAllDomains(libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_ACTIVE)
    cpu_usages = []
    for dom in doms:
        try:
            cpu_stat_1 = dom.getCPUStats(True)[0]
            time.sleep(1)
            cpu_stat_2 = dom.getCPUStats(True)[0]
        except libvirt.libvirtError: 
            continue
        cpu_percent = 100 * ((cpu_stat_2['cpu_time'] - cpu_stat_1['cpu_time']) / 1000000000) 
        cpu_usages.append(round(cpu_percent/len(dom.vcpus()[0]), 2))
    conn.close()
    if len(cpu_usages) == 0:
        return 0
    return round(sum(cpu_usages)/len(cpu_usages), 2)


if __name__ == "__main__":
    # spawnVM()
    while 1:
        print(reportCPUUsage())

    


