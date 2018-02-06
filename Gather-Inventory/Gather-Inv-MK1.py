from jnpr.junos import Device
import sys

# Default Username used is root. This can be changed if you'd rather use a separate account

username = 'root'


def GatherInv(password,switchlist='switchlist-complete',outputfile='switchinv'):

    """
    Summary: Gathers Virtual Chassis Status from a list of switches provided.
    Usage: python Gather-Inv-MK1.py rootpass switchsourcelist outputfile """

    invbuild = open(outputfile, 'w+')

    with open(switchlist) as infile:
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
                    print(' ')
            invbuild.write(64*"=" + '\n')
            invbuild.close()
            dev.close()


if __name__ == "__main__":
    GatherInv(sys.argv[1],sys.argv[2],sys.argv[3])

