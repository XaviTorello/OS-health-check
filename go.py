#/usr/bin/python

from os_health_check import Connection, Check

import logging
import optparse


parser = optparse.OptionParser()

parser.add_option('-H', '--host', dest="host", help="host")
parser.add_option('-P', '--port', dest="port", help="port", default=22, type="int")
parser.add_option('-C', '--check', dest="check", help="check name")
parser.add_option('-l', '--user', dest="user", help="username to login")
parser.add_option('-p', '--pass', dest="password", help="password to login")
parser.add_option('-c', '--cert', dest="cert", help="cert to login")
parser.add_option('-D', '--debug', dest="debug", help="activate debug messages", action="store_true")
parser.add_option('-I', '--info', dest="info", help="activate info messages", action="store_true")

options, args = parser.parse_args()

if not options.host:
    options.host="localhost"

if not options.user:
    options.user="user"

if not options.password:
    options.password="password"

if not options.check:
    options.check = "process_listener 22 1"

if options.info:
    logging.basicConfig(level=logging.INFO)

if options.debug:
    logging.basicConfig(level=logging.DEBUG)


local = Connection(options.host, options.user, options.password, 22)

#cpu = Check(local, ["disk", "swap", "cpu", "process_grep_count portal 4"])
control = Check(local, [options.check], )

local.close_connection()

exit(control.rc)
