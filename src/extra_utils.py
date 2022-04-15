import os, sys

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

def signal_handler(sig, frame):
    clearConsole()
    print("Program has been Terminated.")
    sys.exit(0)