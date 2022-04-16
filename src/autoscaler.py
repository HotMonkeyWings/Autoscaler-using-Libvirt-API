# TODO:
# 1. Spawn VMs
# 2. Report CPU Usage
# 3. Algorithm to spawn new VM
import libvirt
import time
import signal

from extra_utils import checkNewVMs, clearConsole, signal_handler
from configs import LOAD_CONFIG

# Spawn a new VM if available.
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
        return False

    print("New VM:", inactiveDoms[0].name(), "has been booted up.")
    print("Waiting for VM to start. Sleeping for 30 seconds...")
    inactiveDoms[0].create()
    time.sleep(25)
    conn.close()
    return True

# Report the CPU Usages
def reportCPUUsage():
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)
    
    # Get all active domains
    doms = conn.listAllDomains(libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_ACTIVE)

    if len(doms) == 0:
        time.sleep(1.5)
        return [], 0

    # Initialize variables
    delay = 1.5 / len(doms)
    cpu_usages = []

    # Iter through all VMs
    for dom in doms:
        # Get CPU Clock Time in nanoseconds
        try:
            cpu_stat_1 = dom.getCPUStats(True)[0]
            time.sleep(delay)
            cpu_stat_2 = dom.getCPUStats(True)[0]
        except libvirt.libvirtError: 
            continue

        # Calculate CPU Percent from CPU Clock Times
        cpu_percent = 100 * ((cpu_stat_2['cpu_time'] - cpu_stat_1['cpu_time']) / (delay * 10**9)) 
        cpu_percent = 100 if cpu_percent > 100 else cpu_percent
        cpu_usages.append(round(cpu_percent/len(dom.vcpus()[0]), 2))

    conn.close()
    return cpu_usages, len(cpu_usages)

def autoscaler():
    # load_map determines scale up
    load_map = [1] * 5
    load_map_index = 0
    
    while 1:
        cpu_usages, vmcount = reportCPUUsage()
        if vmcount == 0:
            clearConsole()
            print('No VMs online.')
            spawnVM()
            continue

        # If new VMs, restart
        if checkNewVMs(vmcount):
            continue

        # Display CPU Usages
        clearConsole()
        print('[CTRL + C] to Terminate.\n\n')
        for i, cpu in enumerate(cpu_usages):
            print(f"VM {i+1}: {cpu}%")
        cpu_usage = round(sum(cpu_usages)/len(cpu_usages), 2)
        print(f"\nAverage CPU Usage: {cpu_usage}%")

        # Adjust load map depending on CPU usage
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
            if not spawnVM():
                continue
            print("Load Balancer has resumed.")
            time.sleep(1)
            load_map = [1] * 5
    
        print(load_map)
        load_map_index = (load_map_index + 1) % 5
        print(load_map_index*3*" "+" ^")


if __name__ == "__main__":
    # spawnVM()
    clearConsole()
    print("Starting Auto Scaler...")
    signal.signal(signal.SIGINT, signal_handler)
    autoscaler()