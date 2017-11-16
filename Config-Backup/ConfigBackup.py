
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from getpass import getpass
import datetime as dt
import os

username = 'root'
password = getpass("Root Password:")


#Open file named switchlist-Complete 
with open('switchlist-Complete') as infile:
        for host in infile:
                try:

		    
		    dev = Device(host=host.strip(), user=username, password=password)
		    print 'Working on:' , host
		    dev.open()
		    date = dt.datetime.today().strftime("%m-%d-%Y")
		    config = dev.rpc.get_config(options={'format':'text'})
                    #Destination location for Config backups
		    ConfigFile = '/' + date + "/" + host.strip() + '.txt'
		    a = os.path.dirname(ConfigFile)
		    if not os.path.exists(a):
		        os.makedirs(a)
		    from lxml import etree

		    f = open(ConfigFile, 'w')
		    f.write(etree.tostring(config))
		    f.close()
		    dev.close()
		except Exception,e: print "Error:", e
		continue

