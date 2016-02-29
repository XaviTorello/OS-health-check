#/usr/bin/python
from __future__ import division
import paramiko


import logging
logger = logging.getLogger(__name__)


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
    critical = "82"
    warning = "75"

    estats = {'w':'Warning', 'c':'Critical', 'o':'OK'}
    estats_rc = {'w':1, 'c':2, 'o':0}
    estat='o'

    sortida=''

    rc = 0


    def __init__(self, connection, checklist):
        self.connection = connection
        self.trigger_checks(checklist)
        #self.check_proc()

    def trigger_checks(self, checks):
        for check in checks:
            quin_check="check_"+check
            print "Executing {}:\n".format(quin_check)
            control = getattr(Check, quin_check)
            control(self)
            print "Command {} status: {}".format(self.command, self.rc)
            print self.sortida


    def execute_check(self):
        self.connection.launch_command(self.command)


    def check_cpu (self):
        self.command="cat /proc/cpuinfo"
        self.execute_check()
        print self.connection.print_last_command()


    def check_disk (self):
        self.command="df"
        self.execute_check()
        #print self.connection.print_last_command()
        header=1
        self.estat=self.estats_rc['o']
        self.sortida=''


        for linia in self.connection.last_command[2]:
            if header:
                header=0
                continue

            entrada=linia.split()

            entrada[4]=entrada[4].replace('%','')

            self.estat='o'

            if int(entrada[4])>=int(self.critical):
                self.estat = 'c'
            elif int(entrada[4])>=int(self.warning):
                self.estat = 'w'

            missatge="[{}] Disk {} is {}% used\n".format(self.estats[self.estat], entrada[0],entrada[4])

            logger.info(missatge)

            if self.estat != 'o':
                self.sortida+=missatge
                self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))



    def check_swap (self):
        self.command="cat /proc/meminfo | grep Swap"
        self.execute_check()
        #print self.connection.print_last_command()

        self.estat='o'
        self.sortida=''
        self.rc=self.estats_rc['o']

        swapFree=0
        swapTotal=0
        swapUsed=0

        for linia in self.connection.last_command[2]:
            entrada=linia.split()

            if "SwapTotal" in entrada[0]:
                swapTotal = int(entrada[1])
                logger.debug("Swap total: {}{}".format(swapTotal, entrada[2]))

            if "SwapFree" in entrada[0]:
                swapFree = int(entrada[1])
                logger.debug("Swap free: {}{}".format(swapFree, entrada[2]))

        if swapFree and swapTotal>0:
            swapUsed=100-(swapFree*100/swapTotal)
            logger.debug("Swap used: {}%".format(swapUsed))
            print swapUsed



        self.estat='o'

        if swapUsed>=int(self.critical):
            self.estat = 'c'
        elif swapUsed>=int(self.warning):
            self.estat = 'w'

        logger.info("- [{}] Swap is {}% used\n".format(self.estats[self.estat], swapUsed))

        if self.estat != 'o':
            self.sortida+= "{}! - Swap is {}% used\n".format(self.estats[self.estat], swapUsed)
            self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))
