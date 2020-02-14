if __name__ == '__main__':

    from datetime import datetime
    from itertools import zip_longest
    from snmp_update.ironpysnmp_class import *

    ip_address_host = '192.168.111.29'
    port_host = 3

    snmp = IronSNMP()

    start_time = datetime.now()

    print("IP:\t\t\t {0}\nport:\t\t {1}\n".format(ip_address_host, port_host))

    sysDescr = snmp.get_sysdescr(ip_address_host)
    print('title:\t\t', sysDescr)

    sysName = snmp.get_sysname(ip_address_host)
    print('sysname:\t', sysName)

    sysLoc = snmp.get_location(ip_address_host)
    print('sysloc:\t\t', sysLoc)

    uptime = snmp.get_sysuptime(ip_address_host)
    print('\nuptime:\t\t', uptime)

    pst = snmp.get_port_status(ip_address_host, port_host)
    print('port status:', pst)

    speed = snmp.get_port_speed(ip_address_host, port_host)
    print('speed:\t\t', speed)

    rx, tx = snmp.get_errors(ip_address_host, port_host)
    print("\n{0:>22}{1:>32}".format('RX Frames', 'TX Frames'))
    for x, y in zip_longest(rx, tx):
        print('{0:<12} {1:<19}'.format(x, rx[x]), end='')
        if y is not None:
            print('{0:<12} {1:<9}'.format(y, tx[y]))

    mac = snmp.get_port_mac(ip_address_host, port_host)
    print('\n\naddresses:')
    for i in range(len(mac)):
        print('\t\t\t MAC: {1}\tVLAN: {0}'.format(mac[0][i], mac[1][i]))

    print('\nSpent time:', datetime.now() - start_time)

    # [print(i, snmp_get_bulk('192.168.110.87', 'public', 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')[0]) for i in range(1000)]
    # ip = '192.168.110.87'
    # port = 7
