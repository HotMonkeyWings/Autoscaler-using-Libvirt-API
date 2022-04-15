import threading, queue, random, time
import signal, sys, os, socket
import libvirt

# Configs
DELAY_CONFIG = {
    1: ("Low", 0.5),
    2: ("Medium", 0.1),
    3: ("High", 0.03),
    4: ("Very High", 0.001)
}

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

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
        print("New VMs started. Sleeping for 30 seconds...")
        time.sleep(30)
        print("Requests have resumed!")

    conn.close()
    return doms

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
def sendRequests(speed_queue):
    # Fetch connection addresses
    conn_addrs = updateConnections([], True)

    # Set initial variables
    freq, delay = DELAY_CONFIG[1]
    conn_index = 0
    update_conns_interval = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while 1:
        clearConsole()
        print("[CTRL + C] to Terminate.\n\n")
        print("Number of VMs:", len(conn_addrs))
        print("Load Frequency:", freq)
        # Update the delay if it was changed
        try:
            freq, delay = speed_queue.get_nowait()
        except queue.Empty:
            pass

        # Send request to connection, and update index to next VM
        if conn_index != 0:
            s.sendto(str(random.randint(200, 500)).encode(), conn_addrs[conn_index])
            conn_index = (conn_index + 1) % len(conn_addrs)
        update_conns_interval += 1
        time.sleep(delay)

        # Update connection list every 1 second
        if update_conns_interval >= int(1/delay):
            update_conns_interval = 0
            conn_addrs = updateConnections(conn_addrs)

def signal_handler(sig, frame):
    clearConsole()
    print("Client has been Terminated.")
    sys.exit(0)

if __name__ == "__main__":
    clearConsole()
    signal.signal(signal.SIGINT, signal_handler)

    # Speed queue updates the delay for requests
    speed_queue = queue.Queue()

    # Start thread for sending requests
    t1 = threading.Thread(target=sendRequests, args=(
        speed_queue, ), name='run_loop')
    t1.daemon = True
    t1.start()

    # Start socket for updating the delay
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 8000))

    # Wait for delay updates
    while 1:
        pick_delay, addr = s.recvfrom(1024)
        pick_delay = int(pick_delay.decode())
        speed_queue.put(DELAY_CONFIG[pick_delay])