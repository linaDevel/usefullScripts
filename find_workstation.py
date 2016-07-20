#!/usr/bin/python
import paramiko
import threading
import getpass
import socket
import struct
import sys
import re

IP_REGEX = re.compile(
    "^(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\.){3}"
    "([01]?\\d\\d?|2[0-4]\\d|25[0-5])/([0-2]?\\d|3[0-2])$"
)


def ip2long(ip):
    return struct.unpack(">I", socket.inet_aton(ip))[0]


def long2ip(long):
    return socket.inet_ntoa(struct.pack(">I", long))


class SSHThread(threading.Thread):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

        threading.Thread.__init__(self)

    def run(self):
        try:
            client = paramiko.SSHClient()

            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.host, username=self.user,
                password=self.password, port=22, timeout=15
            )

            stdin, stdout, stderr = client.exec_command('ls -l')
            data = stdout.read() + stderr.read()

            if data is not None:
                print self.host

            client.close()
        except:
            pass

if __name__ == "__main__":
    NETWORK = sys.argv[1] if len(sys.argv) >= 2 else raw_input("Network: ")

    if IP_REGEX.match(NETWORK):
        NET, CIDR = NETWORK.split("/")
        USER = getpass.getuser()
        PASSWORD = getpass.getpass()

        NET_LONG = ip2long(NET)

        for NET_SHIFT in range(2, (2 ** (32 - int(CIDR))) - 1):
            SSHThread(long2ip(NET_LONG + NET_SHIFT), USER, PASSWORD).start()
    else:
        print "Invalid network: '%s'" % NETWORK
