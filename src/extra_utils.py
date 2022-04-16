import os, sys, time
import libvirt

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