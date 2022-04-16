# TODO:
# 1. Spawn VMs
# 2. Report CPU Usage
# 3. Algorithm to spawn new VM
import libvirt
import time

from extra_utils import checkNewVMs

# Threshold values to control VM spawn
LOAD_CONFIG = {
    'a' : 40,
    'b' : 85
}

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
    if len(doms) == 0:
        time.sleep(1.5)
        return 0, 0
    delay = 1.5 / len(doms)
    cpu_usages = []
    for dom in doms:
        try:
            cpu_stat_1 = dom.getCPUStats(True)[0]
            time.sleep(delay)
            cpu_stat_2 = dom.getCPUStats(True)[0]
        except libvirt.libvirtError: 
            continue
        cpu_percent = 100 * ((cpu_stat_2['cpu_time'] - cpu_stat_1['cpu_time']) / (delay * 10**9)) 
        cpu_percent = 100 if cpu_percent > 100 else cpu_percent
        cpu_usages.append(round(cpu_percent/len(dom.vcpus()[0]), 2))
    conn.close()
    return round(sum(cpu_usages)/len(cpu_usages), 2), len(cpu_usages)

def autoscaler():
    # load_map determines scale up
    load_map = [1] * 5
    load_map_index = 0
    
    while 1:
        cpu_usage, vmcount = reportCPUUsage()
        checkNewVMs(vmcount)

        print(cpu_usage)

        if cpu_usage > LOAD_CONFIG['a'] and load_map[load_map_index] == 1:
            load_map[load_map_index] = 2
        elif cpu_usage > LOAD_CONFIG['b']:
            load_map[load_map_index] = 3
        elif cpu_usage < LOAD_CONFIG['b'] and load_map[load_map_index] == 3:
            load_map[load_map_index] = 2
        elif cpu_usage < LOAD_CONFIG['a'] and load_map[load_map_index] == 2:
            load_map[load_map_index] = 1

        if sum(load_map) == 15:
            print("CPU load at maximum. Spawning new VM.")
            print("Sleeping for 30 seconds.")
            spawnVM()
            time.sleep(30)
            print("Load Balancer has resumed.")
    
        load_map_index = (load_map_index + 1) % 5
        print(load_map)


if __name__ == "__main__":
    # spawnVM()
    autoscaler()

    


