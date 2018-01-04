#!/usr/bin/env python
#Created by: Dustin Coy
#            DustinCoyMo@gmail.com
#            Springfield Public Schools
#Designed to be used with Rundeck, so that arguments can be passed directly in as an argument
#Please Make a note that this was build to meet the needs of our enviroment, so some tweaking may be needed in order to make this work for you
#Syntax : "python Rundeck-Upgrader A G" to upgrade an EX-3300 to 12.3R12-S6
import sys
import getpass
import os
import time
import waiting
import smtplib
from jnpr.junos import Device
from jnpr.junos.utils.sw import SW
from jnpr.junos.utils.fs import FS
from jnpr.junos.exception import ConnectError
from lxml import etree
from subprocess import call
from airwaveapiclient import AirWaveAPIClient

#Making use of the Airwave API Module created by mtoshi. You'll need to make an API user in airwave for this to work 
airwaveuser = 'username'
airwavepass = 'password'


#Gather Model for First Arg.  Other Models can be added.
ModelIA = sys.argv[2]


if ModelIA == "A":
    Model='3300'

elif ModelIA == "B":
    Model='2200'



#Gather Version from Second Arg 
InitA = sys.argv[3]


if InitA == "A":
    SoftwareA='12.3R3.4'

elif InitA == "B":
    SoftwareA='12.3R9.4'

elif InitA == "C":
    SoftwareA='12.3R12.4'

elif InitA == "D":
    SoftwareA='14.1X53-D35.3'

elif InitA == "E":
    SoftwareA='15.1R5.5'

elif InitA == "F":
    SoftwareA='15.1R6-S3'

elif InitA == "G":
    SoftwareA='12.3R12-S6'
   

print(sys.argv[1])  
print(sys.argv[2])
print(sys.argv[3])

#URL for Airwave Posts


url = 'https://IP-For-Airwave'
PostMessage = '&down_status_message=Scheduled+Software+Upgrades&auto_clear_down_status_message=1'
PreMessage = '/down_status_message.xml?ap_id='
GETIDpre = 'https://IP-For-Airwave/ap_search.xml?query='

#Start Install

def main():


    #Set Software Install Location
    SoftwareB = '/Located-To-Images/jinstall-ex-' + Model + '-' + SoftwareA + '-domestic-signed.tgz'
    print '======================================='

    print('Installing Package ',SoftwareB) 
    log = 'Completed'
    for hostname in sys.argv[1:2]:

        try:
            print '======================================'
            print('Starting Install on ' + hostname)
            dev = Device(host=hostname, user='root', password='random-password')
            dev.open()
            
            # Airwave Process - Still a work in progress
            try:
                airwave = AirWaveAPIClient(username=airwaveuser,password=airwavepass,url=url)
                airwave.login()
                GETIDpost=(GETIDpre + hostname)
                GETIDRES = airwave.session.get(GETIDpost, verify=False)
                GETIDxml = GETIDRES.text
                GETIDMATCHstart = '<record id="'
                GETIDMATCHend = '">'
                SwitchID = (GETIDxml.split(GETIDMATCHstart))[1].split(GETIDMATCHend)[0]
                print('Switch ID is = ' + SwitchID) 
                MessageURL = url + PreMessage + SwitchID + PostMessage
                airwave.session.get(MessageURL, verify=False)
                airwave.logout()
            except:
                print('Failed to make Airwave changes')
            # Started Clearing out the /var/home directory on switches to ensure there aren't any residual files that can cause the switch to run out of space during the upgrade. Currently just does the master RE. Going to rewrite for multiple switches in a VC
            FSA = FS(dev)
            try:
                print 'Cleaning Home Files'
                FSA.rm('/var/home/jinstall*')
            except:
                print 'Local Files Check out'


            try:
                print 'Cleaning Home Files'
                FSA.rm('/var/tmp/jinstall*')
            except:
                print 'Local Files Check out'



            time.sleep(10)
            # Validates Member 0 is master. Typically Member 0 has the uplink, so its vital this switch becomes master before the upgrade starts.

            print '======================================='
            print 'Validating Member 0 is Master of VC'
            DevLookup = dev.facts.get('RE0')
            CurMSTR = DevLookup['mastership_state']
            if ( CurMSTR == 'master' ):
                print '======================================='
                print 'Master is Member 0'
            else:
                print 'Meber 0 is not Master. Performing Master Change Operation'
                dev.cli ("request chassis routing-engine master switch no-confirm",format='xml',warning=False)
                time.sleep(20)
                print 'RE Swapped. Resuming Install'
                dev = Device(host=hostname, user='root', password='random-password')
                dev.open()

            #Does a Pre-Upgrade LLDP Check. Useful for most upgrade analysis
            print '======================================='
            print 'Gathering LLDP Neighbors'
            try:
                PreLLA = dev.rpc.get_lldp_neighbors_information()
                PreLLB = etree.tostring(PreLLA)
            except:
                print 'LLDP service isnt running' #Added for 15.1R5 since there's a bug that crashes LLDP constantly
                PreLLB = '3'	

            sw = SW(dev)	
            ok = sw.install(package=SoftwareB, progress=True)
            #Process for Post Install
            if ok:
                print '======================================'
                print 'Rebooting to complete Install'
                sw.reboot()
                time.sleep(10)	
                waiting =True
                print '======================================='
                print 'Initializing Reconnect Process'
                print '======================================='
                #Starts the process of waiting for the switch to reboot and upgrade. Kind of an old school aproach, but it gets the job done.
                while waiting:
                    counter =0
                    t = os.system('ping -c 1 ' + hostname)
                    if t == 0:
                        waiting=False
                        print '======================================='
                        print 'Switch is Online again'
                        print '======================================='
                        dev.open()
                        time.sleep(180)
                        print 'Performing Post Install Check'
                        #Does a post upgrade check of LLDP neighbors
                        try:
                            PosLLA = dev.rpc.get_lldp_neighbors_information()
                            PosLLB = etree.tostring(PosLLA)
                        except:
                            PosLLB = '3'
                            

                        if ( PreLLB == '3'):
                            print 'LLDP Service isnt running. Skipping Check'
                        elif ( PreLLB == PosLLB ):
                            print '======================================='
                            print 'LLDP Neighbors Match'
                        else:
                            print '!!Failed LLDP Neighbor Check!!'
                            log = (hostname + ' Failed LLDP Neighbor Check')
                            break
                            print '======================================='
                            #print 'Starting Background Snapshot Script'
                            #Added this in for the sake of it being there. I dont reccomend doing snapshots within the same script as the process can take an hour or so depending on the size of the switch stack. Its better to write a seperate script and have Rundeck run it as a seperate step
                            print 'Completed Upgrade Process for ' + hostname
                            log.write('Completed with ' + hostname)
                    else:
                        counter +=1
                        if counter == 10000: # 166 Minutes Max before script decides the switch isn't coming back
                            waiting = False	
                            log = ('Failed to Contact ' + hostname + ' switch!')                       
                        
        except:
            print 'FAIL'
            log = 'Failed Upgrade'
    else:
        #SMS Notification of failure or completion. Rundeck can do this as well, but this portion was written before we started integrating with Rundeck
        print 'Upgrade Session Complete. Notifying SMS Targets'
        msg = log
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("testemailaddress","testemailpassword")
        server.sendmail("testemailaddress@gmail.com","destinationphone-or-email",msg)
        server.quit()

    exit()

main()
 

