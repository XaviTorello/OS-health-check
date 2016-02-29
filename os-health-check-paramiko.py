#/usr/bin/python

import paramiko

class Connection ():
    """ Connection object
    """
    client = paramiko.SSHClient()
    last_command = []


    def __init__(self, host, user, passwd, port=22):
        self.set_new_connection(host,user,passwd, port)

    def set_new_connection(self, host, user, passwd, port):
        try:
            self.close_connection()
        except:
            print "Error tancant"

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())


        self.client.connect(host, port=port, username=user, password=passwd)

        ## Pending try connection except host, usr/pswd, ...
        #try:
        #except "AuthenticationException":
        #    print "Authentication failed"
        #    raise "AuthenticationFailed"
        #except:
        #    print "error"
        #    self.client.close()


    def launch_command(self,command):
        #last_command = command
        stdin, stdout, stderr = self.client.exec_command(command)
        self.last_command =  [command, stdin, stdout, stderr]
        return self.last_command

    def print_last_command (self):
        for line in self.last_command[2]:
            print line.strip('\n')

    def close_connection(self):
        self.client.close()



class Check():

    def __init__(self, connection, checklist):
        self.connection = connection
        self.trigger_checks(checklist)
        self.check_proc()

    def trigger_checks(self, checks):
        for check in checks:
            print check


    def execute_check(self):
        self.connection.launch_command(self.command)

    def check_proc (self):
        self.command="cat /proc/cpuinfo"
        self.execute_check()
        print self.connection.print_last_command()








user="user"
password="password"
host="localhost"

#local = Connection(host, user, password)
local = Connection(host, "gisce", "k")

cpu = Check(local, ["cpu", "disk"])




#local.print_last_command()

local.close_connection()

