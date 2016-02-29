#/usr/bin/python

from os_health_check import Connection, Check



user="user"
password="password"
host="localhost"

#local = Connection(host, user, password)
local = Connection(host, "gisce", "k")

cpu = Check(local, ["disk", "swap"])




#local.print_last_command()

local.close_connection()



