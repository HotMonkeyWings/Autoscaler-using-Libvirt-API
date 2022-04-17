import threading, queue, random, time
import signal, sys, os, socket
import libvirt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from extra_utils import clearConsole, signal_handler, checkNewVMs
from configs import DELAY_CONFIG

AVG_LATENCY = []
FRAME_LEN = 10

# Obtain the IPs of domains.
def getDomainIPs(doms):
    ip_addrs = []
    for dom in doms:
        ifaces = dom.interfaceAddresses(
            libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        for (name, val) in ifaces.items():
            # Skip loopback
            if name == 'lo':
                continue
            ip_addrs.append(val['addrs'][0]['addr'])
    return ip_addrs

# Update the Connections for new VMs
def updateConnections(conn_addrs, initial=False):
    newVMs = checkNewVMs(len(conn_addrs), initial)

    # If no new VMs, return the old address list
    if newVMs == None:
        return conn_addrs

    new_connections = []

    # Get new sockets
    ip_addrs = getDomainIPs(newVMs)
    for ip_addr in ip_addrs:
        new_connections.append((ip_addr, 12345))
    return new_connections


# Send Requests periodically. 
# Change the delay using speed_queue
def sendRequests(speed_queue, s):
    global AVG_LATENCY
    # Fetch connection addresses
    conn_addrs = updateConnections([], True)

    # Set initial variables
    freq, delay = DELAY_CONFIG[1]
    conn_index = 0
    update_conns_interval = 0
    startTime = time.time()
    latency = []

    while 1:
        # Update the Plot
        plt.gcf().canvas.draw_idle()
        plt.gcf().canvas.start_event_loop(0.05)

        # Update the delay if it was changed
        try:
            freq, delay = speed_queue.get_nowait()
        except queue.Empty:
            pass

        # Update connection list every 1 second
        if time.time() - startTime >= 1:
            startTime = time.time()
            conn_addrs = updateConnections(conn_addrs)
            clearConsole()
            print("[CTRL + C] to Terminate.\n\n")
            print("Number of VMs:", len(conn_addrs))
            print("Load Frequency:", freq)
            if AVG_LATENCY:
                print(f"Latency: {AVG_LATENCY[-1]}ms")
                # print(LATENCY)
                # LATENCY = []
                latency = []
            else:
                print("Not sending requests at the moment.")

        # Send request to connection, and update index to next VM
        if len(conn_addrs) != 0:
            msg = str(random.randint(200, 500)) + " " + str(time.time())
            s.sendto(msg.encode(), conn_addrs[conn_index])
            conn_index = (conn_index + 1) % len(conn_addrs)
        update_conns_interval += 1
        time.sleep(delay)


def animateGraph(i):
    plt.cla()
    print(i)
    if len(AVG_LATENCY) <= FRAME_LEN:
        plt.plot(AVG_LATENCY, label=f"Average Latency")
    else:
        plt.plot(AVG_LATENCY[-FRAME_LEN:], label=f"Average Latency")

    plt.ylim(0, 5)
    plt.xlim(0, FRAME_LEN)
    plt.xlabel('Time (s)')
    plt.ylabel('Latency (ms)')
    plt.legend(loc = 'upper right')
    plt.tight_layout()

def speedController():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 8000))

    # Wait for delay updates
    while 1:
        pick_delay, addr = s.recvfrom(1024)
        pick_delay = int(pick_delay.decode())
        try:
            speed_queue.put(DELAY_CONFIG[pick_delay])
        except IndexError:
            pass

def latencyCalculator(s):
    startTime = time.time()
    latency = []
    while 1:
        if time.time() - startTime >= 1:
            startTime = time.time()
            AVG_LATENCY.append(sum(latency)/len(latency))
            latency = []
        msg, addr = s.recvfrom(1024)
        msg = msg.decode()
        oldTime = float(msg.split()[-1])
        latency.append((time.time()-oldTime) * 1000)


if __name__ == "__main__":
    clearConsole()
    signal.signal(signal.SIGINT, signal_handler)

    # Speed queue updates the delay for requests
    speed_queue = queue.Queue()

    # Start thread for sending requests
    print("Starting Client...")
    ani = FuncAnimation(plt.gcf(), animateGraph, interval = 1000)
    plt.show(block=False)

    # Start Speed Controler
    speedControlThread = threading.Thread(target=speedController, name='Speed Controller')
    speedControlThread.daemon = True
    speedControlThread.start()


    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 9000))

    latencyCalculatorThread = threading.Thread(target=latencyCalculator, args=(s,), name='Latency Calculator')
    latencyCalculatorThread.daemon = True
    latencyCalculatorThread.start()

    sendRequests(speed_queue, s)
    # Start socket for updating the delay