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
	self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
            execucio=check.split(" ")
            logger.debug("Triggering {}".format(execucio))

            quin_check="check_"+execucio[0]
            logger.debug("Executing {}:".format(quin_check))
            control = getattr(Check, quin_check)
            control(self, execucio)
            logger.debug("Command {} status: {}".format(self.command, self.rc))
            print self.sortida


    def execute_check(self):
        self.connection.launch_command(self.command)

    def check_process_listener (self, params=None):
        tcp_port = str(params[1])

        try:
            count_expected = int(params[2])
        except:
            logger.info("No expected count received, setting to 1")
            count_expected = 1

        try:
            tcp6_avoid = bool(params[3])
        except:
            logger.info("No tcp6_avoid received, setting to True to avoid review tcp6 listeners")
            tcp6_avoid = "True"

        self.command="/bin/netstat -tan | egrep -e 'LISTEN|ESCUCH' | grep {}".format(tcp_port)

        if tcp6_avoid == "True":
            self.command+=" | grep -v tcp6"

	logger.info("Executing: '{}'".format(self.command))
        self.execute_check()

        count=0
        listeners=[]
        self.estat='o'
        self.sortida=''
        self.rc=self.estats_rc['o']

        for linia in self.connection.last_command[2]:
            logger.info(" - {}".format(linia))
            listeners.append(str(linia.split()[3]))
            count+=1

        def compare(x):
            return {
                count_expected: 'o',
                0: 'c',
            }.get(x,'u')

        self.estat=compare(count)

        if self.estat == 'u':  #si no es l'esperat o 0
            if (count<count_expected):
                self.estat='c'
            else:
                self.estat='w'

        missatge = "[{}] There are {} listener for port '{}' ({}). Expected count: {}".format(self.estats[self.estat], count, tcp_port, listeners, count_expected)

        self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))
        self.sortida+= missatge



    def check_process_grep_count (self, params=None):
        process_exp = str(params[1])
        count_expected = int(params[2])

        self.command="pgrep -fc {}".format(process_exp)
        self.execute_check()
        #print self.connection.print_last_command()

        self.estat='o'
        self.sortida=''
        self.rc=self.estats_rc['o']

        for linia in self.connection.last_command[2]:
            count=int(linia.split()[0])

        def compare(x):
            return {
                count_expected: 'o',
                0: 'c',
            }.get(x,'u')

        self.estat=compare(count)

        if self.estat == 'u':  #si no es l'esperat o 0
            if (count>count_expected):
                self.estat='c'
            else:
                self.estat='w'


        missatge = "[{}] The count of '{}' is {}. Expected count: {}".format(self.estats[self.estat], process_exp, count, count_expected)
        #logger.info("Load average is {}, {}, {}".format(avg1, avg5, avg15))


        #if self.estat != 'o':
        self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))
        self.sortida+= missatge


    def check_cpu (self, params=None):
        #get the number of cpus
        self.command="cat /proc/cpuinfo | grep processor | wc -l"
        self.execute_check()
        for linia in self.connection.last_command[2]:
            entrada=linia.split()
            cpus=float(entrada[0])

        logger.info("This OS have {} cpus.".format(int(cpus)))

        self.command="cat /proc/loadavg"
        self.execute_check()
        #print self.connection.print_last_command()

        self.estat='o'
        self.sortida=''
        self.rc=self.estats_rc['o']

        avg1 = 0.0
        avg5 = 0.0
        avg15 = 0.0

        warning_threshold = [ 0.9, 0.75, 0.5 ]
        critical_threshold = [ 0.99, 0.8, 0.6 ]

        logger.info("Warning threshold is {} (For each CPU: {})".format([x * cpus for x in warning_threshold], warning_threshold))
        logger.info("Critical threshold is {} (For each CPU: {})".format([x * cpus for x in critical_threshold], critical_threshold))
        processes = 0
        total_processes = 0
        last_pid = 0

        for linia in self.connection.last_command[2]:
            entrada=linia.split()

            #print entrada[0]
            avg1, avg5, avg15 = entrada[0], entrada[1],entrada[2]

            processes,total_processes = entrada[3].split("/")
            last_pid=entrada[4]

            logger.info("Load average is {}, {}, {}".format(avg1, avg5, avg15))
            logger.info("Processes: {} of {}. Last PID: {}".format(processes, total_processes, last_pid))

        self.estat='o'

        def review_threshold(actuals, warn, crit, cpu):
            rc=0
	    rc='o'
            for idx, actual in enumerate(actuals):
	        if float(actual)>float(crit[idx] * float(cpu)): #if critical return it directly!
                    logger.info("- [{}] Load average is {} for the last {}".format(self.estats['c'], float(actual),idx))
	            return 'c'
	        elif float(actual)>float(crit[idx] * float(cpu)):
	       	    rc='w'
                logger.info("- [{}] Load average is {} for the last {}".format(self.estats[rc], float(actual),idx))
            return rc


        self.estat=review_threshold([avg1, avg5, avg15] , critical_threshold, warning_threshold, cpus)

        #if self.estat != 'o':
        self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))
        self.sortida+= "[{}] Load average is {}, {}, {} [{} cpus] (threshold {}, per cpu {})".format(self.estats[self.estat], avg1, avg5, avg15, int(cpus), [x * cpus for x in critical_threshold], critical_threshold)



    def check_erp_version (self, params=None):
        pathh = "/home/erp/src/erp/"
        self.command="/usr/bin/git -C " + pathh + " describe --tag"
        self.execute_check()
        #print self.connection.print_last_command()
        header=1
        self.estat=self.estats_rc['o']
        self.sortida=''
        missatge=""
        count = 0

        self.estat='o'

        for linia in self.connection.last_command[2]:
            count += 1
            entrada=linia.split()

            self.estat='o'
            missatge="[{}] ERP {} is at {} tag\n".format(self.estats[self.estat], pathh, entrada[0])

            logger.info(missatge)

        if count < 1:
            self.estat='w'
            missatge="[{}] Not found any ERP in {}\n".format(self.estats[self.estat], pathh)
            logger.info(missatge)

        self.sortida+=missatge
        self.rc=self.estats_rc[self.estat]



    def check_disk (self, params=None):
        self.command="df -h"
        self.execute_check()
        #print self.connection.print_last_command()
        header=1
        self.estat=self.estats_rc['o']
        self.sortida=''

        critical = "95"
        warning = "85"

        for linia in self.connection.last_command[2]:
            if header:
                header=0
                continue

            entrada=linia.split()

            entrada[4]=entrada[4].replace('%','')

            self.estat='o'

            if int(entrada[4])>=int(critical):
                self.estat = 'c'
                if (entrada[0]).find("/")>-1:  #for smb mountpoints set warning instead of critical
                    self.estat = 'w'

            elif int(entrada[4])>=int(warning):
                self.estat = 'w'

            missatge="[{}] Disk {} is {}% used on {}. Available: {}\n".format(self.estats[self.estat], entrada[0],entrada[4], entrada[5], entrada[3])

            logger.info(missatge)

            if self.estat != 'o':
                self.sortida+=missatge
                self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))



    def check_swap (self, params=None):
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



        self.estat='o'

        if swapUsed>=int(self.critical):
            self.estat = 'c'
        elif swapUsed>=int(self.warning):
            self.estat = 'w'

        missatge="[{}] Swap is {}% used\n".format(self.estats[self.estat], swapUsed)
        logger.info(missatge)

        # if self.estat != 'o':
        self.sortida+= missatge
        self.rc=max(int(self.rc), int(self.estats_rc[self.estat]))
