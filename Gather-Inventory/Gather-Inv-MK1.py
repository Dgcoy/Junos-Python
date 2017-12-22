import yaml
from passlib.hash import md5_crypt
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from getpass import getpass
from lxml import etree


import time
import logging
import sys

username = 'root'
password = getpass("Root Password:")
try:
    os.remove('/home/administrator/Projects/Reference-Data/Rundeck-Switches.json')
except:
    print 'Nothing to remove'
invbuild = open('/home/administrator/Projects/Reference-Data/SwitchInv', 'w+')

with open('/home/administrator/Projects/Reference-Data/switchlist-Complete') as infile:
    for host in infile:

        dev = Device(host=host.strip(), user=username, password=password)
        dev.open()

        rsp = dev.rpc.get_virtual_chassis_information()		
        switchnamepre = dev.rpc.get_software_information(normalize=True)
        switchname = switchnamepre.xpath(".//host-name")[0].text
        invbuild.write(64*"=" + '\n')
        invbuild.write('Switch Name: ' + switchname + '\n') 
        invbuild.write(64*"=" + '\n')
        for id in range(10):
            try:
        
                invbuild.write('Member ID: ' + (rsp.xpath(".//member-id")[id].text) + '\n')
                invbuild.write('Serial: ' + (rsp.xpath(".//member-serial-number")[id].text) + '\n')
                invbuild.write('VC Status: ' + (rsp.xpath(".//member-status")[id].text) + '\n')
            except:
                print ' '
        invbuild.write(64*"=" + '\n')
        dev.close()
