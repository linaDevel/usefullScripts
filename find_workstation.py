#!/usr/bin/python
import paramiko
import threading
import getpass
import sys


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
            client.connect(hostname=self.host, username=self.user, password=self.password, port=22, timeout=15)
            stdin, stdout, stderr = client.exec_command('ls -l')
            data = stdout.read() + stderr.read()

            if data is not None:
                print self.host

            client.close()
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for i in range(2, 126):
            USER = getpass.getuser()
            PASSWORD = getpass.getpass()

            SSHThread("%s.%s" % (sys.argv[1], i), USER, PASSWORD).start()
    else:
        print "No network specified"

