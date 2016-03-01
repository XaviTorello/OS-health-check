#/usr/bin/python

from os_health_check import Connection, Check


import logging
logging.basicConfig(level=logging.INFO)

user="user"
password="password"
host="host"

#local = Connection(host, user, password)
local = Connection(host, "gisce", "k")

#cpu = Check(local, ["disk", "swap", "cpu"])
control = Check(local, ["process_grep_count portal 4"], )

#local.print_last_command()

local.close_connection()

exit(control.rc)