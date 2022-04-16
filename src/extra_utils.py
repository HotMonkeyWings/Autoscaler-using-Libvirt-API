import os, sys, time
import libvirt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class DynamicGraph:
    def __init__(self):
        self.y = {}
        self.frame_len = 30
        self.fig = plt.figure(figsize=(6, 2))
    
    def update(self, cpu_usages):
        for name in cpu_usages:
            if name not in self.y:
                self.y[name] = []
            self.y[name].append(cpu_usages[name])
        
    def plotGraph(self, i):
        plt.cla()
        for name in self.y:
            if len(self.y[name]) > self.frame_len:
                plt.plot(y[name][-self.frame_len:], label=name+" CPU Usage")
            else:
                plt.plot(y[name], label=name+" CPU Usage")

        plt.ylim(0, 100)
        plt.xlim(0, 30)
        plt.xlabel('Time (s)')
        plt.ylabel('CPU Usage (%)')
        plt.legend(loc = 'upper right')
        plt.tight_layout()

    def startGraph(self):
        ani = FuncAnimation(plt.gcf(), self.plotGraph, interval = 1000)
        plt.show()

# Simple command caller to clear the terminal
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

# Deals with system interrupts
def signal_handler(sig, frame):
    clearConsole()
    print("Program has been Terminated.")
    sys.exit(0)

# Checks for the VMs and update if required
def checkNewVMs(old_connection_count=0, initial=False):
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    doms = conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)

    # No new VMs. Proceed with old set.
    if len(doms) == old_connection_count:
        return None

    # New VMs were spawned, wait for startup.
    elif not initial and len(doms) > old_connection_count:
        print("New VM detected. Sleeping for 30 seconds...")
        time.sleep(29)
        print("Requests have resumed!")
        time.sleep(1)

    conn.close()
    return doms