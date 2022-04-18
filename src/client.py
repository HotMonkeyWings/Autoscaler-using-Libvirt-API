import threading, queue, random, time, multiprocessing
import signal, sys, os, socket
import libvirt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from extra_utils import clearConsole, signal_handler, checkNewVMs
from configs import DELAY_CONFIG

# Configuration Values
AVG_LATENCY = []
FRAME_LEN = 30
REQUESTS_PER_CYCLE = 50

# Obtain the IPs of domains.
def getDomainIPs(doms):
    ip_addrs = []
    for dom in doms:
        try:
            ifaces = dom.interfaceAddresses(
                libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        except libvirt.libvirtError:
            continue
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

    # Start new threads for listening to VMs
    new_threads = len(newVMs) - len(conn_addrs)
    for _ in range(new_threads):
        for i in range(5):
            captureResponseThread = threading.Thread(target=captureResponses, args=(s,))
            captureResponseThread.daemon = True
            captureResponseThread.start()

    # Get new IP Addresses
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
            conn_addrs = updateConnections(conn_addrs, s)
            clearConsole()
            print("[CTRL + C] to Terminate.\n\n")
            print("Number of VMs:", len(conn_addrs))
            print("Load Frequency:", freq)
            print("Requests per second:", REQUESTS_PER_CYCLE/delay)
            if AVG_LATENCY:
                print(f"Latency: {AVG_LATENCY[-1]}ms")
                latency = []
            else:
                print("Not sending requests at the moment.")

        # Send request to connection, and update index to next VM
        if len(conn_addrs) != 0:
            # Produce Random Numbers with Time request was sent.
            msg_list = [str(random.randint(200, 500)) + " " + str(time.time()) for i in range(REQUESTS_PER_CYCLE)]
            for msg in msg_list:
                s.sendto(msg.encode(), conn_addrs[conn_index])
            conn_index = (conn_index + 1) % len(conn_addrs)

        time.sleep(delay)


# Captures responses from servers
def captureResponses(s):
    global AVG_LATENCY

    # Initialize variables
    startTime = time.time()
    latency = []

    # Start capturing
    while 1:
        # Update AVG_LATENCY every 1 second
        if time.time() - startTime >= 1:
            startTime = time.time()
            AVG_LATENCY.append(sum(latency)/len(latency))
            latency = []

        # Receive the response
        msg, addr = s.recvfrom(1024)
        msg = msg.decode()

        # Calculate the latency
        oldTime = float(msg.split()[-1])
        latency.append((time.time()-oldTime) * 1000)

# Helps to animate the graph
def animateGraph(i):
    plt.cla()
    if len(AVG_LATENCY) <= FRAME_LEN:
        plt.plot(AVG_LATENCY, label=f"Average Latency")
    else:
        plt.plot(AVG_LATENCY[-FRAME_LEN:], label=f"Average Latency")

    plt.ylim(0, 30)
    plt.xlim(0, FRAME_LEN)
    plt.xlabel('Time (s)')
    plt.ylabel('Latency (ms)')
    plt.legend(loc = 'upper right')
    plt.tight_layout()

# Helps to change request speed.
def speedController():

    # Setup socket
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

    sendRequests(speed_queue, s)