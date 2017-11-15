from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from getpass import getpass
import time

username = 'root'
password = getpass("Root Password:")
# Snapshot .conf file
conf_file = 'Snapshot.conf'


#Open a file called swichlist which has a list of devices to modify
with open('switchlist') as infile:
        for host in infile:
                try:
                        print "Working on:", host,
                       
			#Connect to devices in switchlsit file using username and password provided above
                        
			dev = Device(host=host.strip(),  user=username, password=password)
                        dev.open()
        		dev.timeout = 300    
			cu = Config(dev)
			
			
			
			print "Loading configuration changes"
			
			cu.load(path=conf_file, merge=True)
			
       		        
			
	
            		cu.commit(confirm=5)
                        print "Completed initial commit on:", host
			print "120 seconds until validation if connection is still present"
			time.sleep(120) #wait for 120 seconds
			cu.commit()
			print "Connection Live on:", host , "Moving On" 
			dev.close()

                except Exception,e: print "Error:", e
                continue
