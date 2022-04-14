#!/usr/bin/python
import sys
import libvirt

# This opens the most flexible connection.
# Takes an extra parameter containing authentication
# credentials for the Application.
# Helps application to request a read-only connection 
# using vir_connect_ro flag.

SASL_USER = 'virt'
SASL_PASS = 'epicburger'

def request_cred(credentials, user_data):
    for credential in credentials:
        print(credential)
        if credential[0] == libvirt.VIR_CRED_AUTHNAME:
            credential[4] = SASL_USER
        elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
            credential[4] = SASL_PASS
    return 0

auth = [[ libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], request_cred, None]

conn = None
try:
    conn = libvirt.openAuth('qemu+tcp://localhost/system', auth, 0)
except libvirt.libvirtError as e:
    print(repr(e), file=sys.stderr)
    exit(1)
conn.close()
exit(0)
