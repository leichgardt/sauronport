if __name__ == '__main__':

    from datetime import datetime
    from itertools import zip_longest
    from api.iron_pysnmp_class import *

    # ip_address_host = '192.168.111.29'  # DES-3200 servernaya
    # ip_address_host = '192.168.110.246'  # SNR
    # ip_address_host = '192.168.110.232'  # SNR (old firmware)
    # ip_address_host = '192.168.111.111'  #
    # ip_address_host = '192.168.111.12'  # aggregation
    # ip_address_host = '192.168.100.55'  # cisco L-3
    # ip_address_host = '192.168.110.190'  # DES-3028
    # ip_address_host = '192.168.110.87'
    ip_address_host = '192.168.110.71'
    # ip_address_host = '192.168.111.2'
    port_host = 25

    snmp = IronSNMP()

    start_time = datetime.now()

    print("IP:\t\t\t {0}\nport:\t\t {1}\n".format(ip_address_host, port_host))

    sysName = snmp.get_sysname(ip_address_host)
    print('sysname:\t', sysName)

    sysDescr = snmp.get_sysdescr(ip_address_host)
    print('title:\t\t', sysDescr)

    sysLoc = snmp.get_syslocation(ip_address_host)
    print('sysloc:\t\t', sysLoc)

    uptime = snmp.get_sysuptime(ip_address_host)
    print('uptime:\t\t', uptime)

    pst = snmp.get_port_status(ip_address_host, port_host)
    print('\nport status:', pst)

    ptg = snmp.vlan_tag_check(ip_address_host, port_host)
    print('port tagged:', ptg)

    plk = snmp.get_port_link(ip_address_host, port_host)
    print('port link:\t', plk)

    speed = snmp.get_port_speed(ip_address_host, port_host)
    print('speed:\t\t', speed)

    mac, vlan = snmp.get_port_mac(ip_address_host, port_host)
    if 'n/a' in mac or 'n/a' in vlan:
        print('\n\naddresses is n/a')
    else:
        print('\naddresses:')
        for i in range(0, len(mac)):
            print('\t\t\t MAC: {1}\tVLAN: {0}'.format(mac[i], vlan[i]))

    rx, tx = snmp.get_errors(ip_address_host, port_host)
    print("\n{0:>22}{1:>42}".format('RX Frames', 'TX Frames'))
    for x, y in zip_longest(rx, tx):
        print('{0:<12} {1:<19}'.format(x, rx[x]), end='')
        print('{0:<22} {1:<9}'.format(y, tx[y])) if y is not None else print()
    print()

    print('\n\nSpent time:', datetime.now() - start_time)
