from snmp_update.ironpysnmp import *

ip_address_host = '192.168.111.29'
port_host = 3

print("IP:\t\t\t {0}\nport:\t\t {1}\n".format(ip_address_host, port_host))

sysDescr = snmp_get_sysdescr(ip_address_host)
print('title:\t\t', sysDescr)

sysName = snmp_get_sysname(ip_address_host)
print('sysname:\t', sysName)

pst = snmp_get_port_status(ip_address_host, port_host, 'public')
print('port status:', pst)

speed = snmp_get_port_speed(ip_address_host, port_host, 'public')
print('speed:\t\t', speed)

mac = snmp_get_port_mac(ip_address_host, port_host, 'public')
print('addresses:')
for i in range(len(mac)):
    print('\t\t\t VLAN: {0}\tMAC: {1}'.format(mac[0][i], mac[1][i]))
