#/usr/bin/python

from os_health_check import Connection, Check

import logging
import optparse

logging.basicConfig(level=logging.DEBUG)



parser = optparse.OptionParser()

parser.add_option('-H', '--host',
    dest="host",
    help="host")

parser.add_option('-c', '--check',
    dest="check",
    help="check name")

options, args = parser.parse_args()

host="abenergia-erp.clients.gisce.lan"
if options.host:
    host = options.host

user="monitoring"
password="monitoring"


check = "process_grep_count portal 4"
if options.check:
    check = options.check



local = Connection(host, user, password, 22)

#cpu = Check(local, ["disk", "swap", "cpu"])
#control = Check(local, ["process_grep_count portal 4"], )
control = Check(local, [check], )

#local.print_last_command()

local.close_connection()

exit(control.rc)
