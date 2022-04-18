# TODO:
# 1. Spawn VMs
# 2. Report CPU Usage
# 3. Algorithm to spawn new VM
import libvirt
import time
import threading
import signal

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from extra_utils import DynamicGraph, checkNewVMs, clearConsole, signal_handler
from configs import LOAD_CONFIG

CPU_USAGE_HISTORY = {}
FRAME_LEN = 30

# Spawn a new VM if available.
def spawnVM():
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    # Obtain all inactive VMs
    inactiveDoms = conn.listAllDomains(libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_INACTIVE)
    inactiveDoms.sort(key=lambda dom: dom.name())

    # If none, return False
    if not inactiveDoms:
        print("No more VMs available!")
        return False


    print("New VM:", inactiveDoms[0].name(), "has been booted up.")
    print("Waiting for VM to start. Sleeping for 30 seconds...")

    # Start the VM
    inactiveDoms[0].create()

    # Report CPU Usage till VM boots up.
    # Here, we use 20 assuming few assumptions instead of 30 seconds
    for i in range(20):
        cpu_usages, vmcount = reportCPUUsage()

        # Update the graph
        updateGraph(cpu_usages)

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
    cpu_usages = {}

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
        cpu_usages[dom.name()] = (round(cpu_percent/len(dom.vcpus()[0]), 2))

    conn.close()
    return cpu_usages, len(cpu_usages)

# Update the graph with new CPU Usage values
def updateGraph(cpu_usages):
    global CPU_USAGE_HISTORY
    for name in cpu_usages:
        if name not in CPU_USAGE_HISTORY:
            CPU_USAGE_HISTORY[name] = [] 
            if CPU_USAGE_HISTORY:
                CPU_USAGE_HISTORY[name] = [0] * len(max(CPU_USAGE_HISTORY.values()))

        CPU_USAGE_HISTORY[name].append(cpu_usages[name])
    
    # Plot updated values
    plt.gcf().canvas.draw_idle()
    plt.gcf().canvas.start_event_loop(0.05)

# Generic function to animate the graph
def animateGraph(i):
    plt.cla()       # Clear the graph

    # Get all VM values
    for name in CPU_USAGE_HISTORY:
        if len(CPU_USAGE_HISTORY[name]) <= FRAME_LEN:
            plt.plot(CPU_USAGE_HISTORY[name], label=f"{name} CPU Usage")
        else:
            plt.plot(CPU_USAGE_HISTORY[name][-FRAME_LEN:], label=f"{name} CPU Usage")

    # Plot configurations
    plt.ylim(0, 100)
    plt.xlim(0, 30)
    plt.xlabel('Time (s)')
    plt.ylabel('CPU Usage (%)')
    plt.legend(loc = 'upper right')
    plt.tight_layout()


def autoscaler():
    # load_map determines scale up
    load_map = [1] * 5
    load_map_index = 0
    cpu_usages = {}

    ani = FuncAnimation(plt.gcf(), animateGraph, interval = 1000)
    plt.show(block=False)
    
    while 1:
        # plt.pause(0.05)
        cpu_usages, vmcount = reportCPUUsage()
        if vmcount == 0:
            clearConsole()
            print('No VMs online.')
            spawnVM()
            continue

        # Update the graph
        updateGraph(cpu_usages)

        # If new VMs, restart
        if checkNewVMs(vmcount):
            continue

        # Display CPU Usages
        clearConsole()
        print('[CTRL + C] to Terminate.\n\n')
        for name in cpu_usages:
            cpu_usages[name] = 100 if cpu_usages[name] > 100 else cpu_usages[name]
            print(f"{name}: {cpu_usages[name]}%")
        cpu_usage = round(sum(cpu_usages.values())/len(cpu_usages.values()), 2)
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