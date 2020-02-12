from pysnmp.hlapi import *

COMMUNITY = 'public'
OID = {'sysName': '1.3.6.1.2.1.1.5.0',  # hostname
       'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',  # ports status
       'ifSpeed': '1.3.6.1.2.1.2.2.1.5',  # ports speed
       'dot1dTpFdbAddress': '1.3.6.1.2.1.17.4.3.1.1',  # mac adress
       'dot1dTpFdbPort': '1.3.6.1.2.1.17.4.3.1.2',  # port
       'sysDescr': '1.3.6.1.2.1.1.1'}


def snmp_get_next(ip, community, oid, mib=''):
    '''
    SNMP request for a one parameter.
    MIB don't needed if use OID. But if use Object Name of OID then MID is needed to specify.
    Using v2c at mpModel=1. "mpMpdel=0" is a v1.
    Community is access level of request.
    '''
    ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
    try:
        (errInd,
         errStat,
         errId,
         varBinds) = next(getCmd(SnmpEngine(),
                                 CommunityData(community, mpModel=1),  # SNMPv2c
                                 UdpTransportTarget((ip, 161), timeout=2.0, retries=0),
                                 ContextData(),
                                 ObjectType(ObjId)))
        if errInd or errStat:
            print('ERROR Ind/Stat from getCmd into snmp_get_next\n', errInd, errStat, errId)
            return 0
        else:
            return varBinds
    except Exception as e:
        print("snmp_get_next: GetCmd exception:\n{0}\n".format(e))
        return 0


def snmp_get_bulk(ip, community, oid, mib=''):
    '''
    SNMP request returns a list of parameters.
    The same, MIB is needed only with ObjName.
    '''
    rez = []
    ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
    try:
        for (errInd,
             errStat,
             errId,
             varT) in bulkCmd(SnmpEngine(),
                              CommunityData(community, mpModel=1),
                              UdpTransportTarget((ip, 161), timeout=10.0, retries=5),
                              ContextData(),
                              0, 25,
                              ObjectType(ObjId),
                              lexicographicMode=False):
            if errInd or errStat:
                print('ERROR Ind/Stat from bulkCmd into snmp_get_bulk\n', errInd, errStat, errId)
                return 0
            else:
                for varL in varT:
                    rez.append(varL)
        return rez
    except Exception as e:
        print("snmp_get_bulk: BulkCmd exception:\n{0}\n".format(e))
        return 0


def snmp_pretty(obj, split_by=' = ', last=True):
    return obj[0].prettyPrint().split(split_by)[-1] if last else obj[0].prettyPrint().split(split_by)


def snmp_get_port_status(ip, port, community=COMMUNITY):
    '''
    Getting a port status at router port x by OID 1.3.6.1.2.1.2.2.1.8.x
    Status: 1-up, 2-down, 3-testing, 4-unknown, 5-dormant, 6-notPresent, 7-lowerLayerDown.
    Using a function snmp_get_next::getCmd for pulling out a one parameter.
    '''
    varBinds = snmp_get_next(ip, community, '1.3.6.1.2.1.2.2.1.8.' + str(port))
    if varBinds is not 0:
        rez = int(snmp_pretty(varBinds))
        print('!!!!!!!!!!!!!!!!!!!!!', rez)
        if rez is 1:
            return 'up'
        elif rez is 2:
            return 'down'
        elif rez is 3:
            return 'testing'
        elif rez is 4:
            return 'unknown'
        elif rez is 5:
            return 'dormant'
        elif rez is 6:
            return 'notPresent'
        elif rez is 7:
            return 'lowerLayerDown'
        else:
            return rez
    else:
        print('GET_PORT_STATUS: snmp_get_next error: the answer is empty.')
        return 0


def snmp_get_port_speed(ip, port, community=COMMUNITY):
    '''
    Getting a port speed at router port x by OID 1.3.6.1.2.1.2.2.1.5.x
    Answer shown as a bit/sec bandwidth, that's why output must be need to translated to Mbit/sec to readability.
    Using a function snmp_get_next::getCmd for pulling out a one parameter.
    '''
    varBind = snmp_get_next(ip, community, '1.3.6.1.2.1.2.2.1.5.' + str(port))
    if varBind is not 0:
        rez = snmp_pretty(varBind).replace(' ', '')
        return str(int(rez) / 1000000) + ' Mbit/s'
    else:
        print('GET_PORT_SPEED: snmp_get_next error: the answer is empty.')
        return 0


def snmp_get_port_mac(ip, port, community=COMMUNITY):
    '''
    Getting a table with MACs and their ports with VLAN.
    ObjName: "dot1qTpFdbPort", MID: "Q-BRIDGE-MIB".
    Using a function snmp_get_next::getBulk for pulling out many parameters.
    '''
    macs = []
    vlans = []
    varTable = snmp_get_bulk(ip, community, 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')
    if varTable is not 0:
        for varBinds in varTable:
            if int(varBinds[1]) == int(port):
                varBind = snmp_pretty(varBinds, '.', False)
                vlans.append(int(varBind[1]))
                macs.append(str(varBind[2][1:-1]))
        return vlans, macs
    else:
        print('GET_PORT_MAC: snmp_get_bulk error: the answer is empty.')
        return 0, 0


def snmp_get_sysdescr(ip):
    return snmp_pretty(snmp_get_bulk(ip, COMMUNITY, OID['sysDescr']))


def snmp_get_sysname(ip):
    return snmp_pretty(snmp_get_next(ip, COMMUNITY, OID['sysName']))


def snmp_get_location(ip):
    return snmp_pretty(snmp_get_bulk(ip, COMMUNITY, 'sysLocation', 'SNMPv2-MIB'))


# def snmp_get_errors(ip, port):
#     '''
#     RX Frames:                  TX Frames:
#         0 - Port ID                 0 - Port ID
#         1 - CRC Error               1 - Excessive Deferral
#         2 - Undersize               2 - CRC Error
#         3 - Oversize                3 - Late Collision
#         4 - Fragment                4 - Excessive Collision
#         5 - Jabber                  5 - Single Collision
#         6 - Drop Pkts               6 - Collision
#         7 - Symbol Error
#     '''
#     varTable = snmp_get_bulk(ip, COMMUNITY, 'etherStatsEntry', 'RMON-MIB')
#     rx_frames = [[] for _ in range(8)]
#     tx_frames = [[] for _ in range(7)]
#     for varBinds in varTable:
#         if


def snmp_get_all_data(ip, port):
    title = snmp_get_sysdescr(ip)
    sysname = snmp_get_sysname(ip)
    sysloc = snmp_get_location(ip)
    status = snmp_get_port_status(ip, port)
    speed = snmp_get_port_speed(ip, port)
    vlans, macs = snmp_get_port_mac(ip, port)
    return title, sysname, sysloc, status, speed, vlans, macs


def snmp_get_update(ip, port):
    status = snmp_get_port_status(ip, port)
    speed = snmp_get_port_speed(ip, port)
    vlans, macs = snmp_get_port_mac(ip, port)
    return status, speed, vlans, macs


from datetime import datetime

# 1.3.6.1.2.1.2.2.1.20
# 1.3.6.1.2.1.16.1.1.1 ERRORSSSSSSS
# RX
# crc 1.3.6.1.2.1.16.1.1.1.8.x
# undersize 1.3.6.1.2.1.16.1.1.1.9.x
# oversize 1.3.6.1.2.1.16.1.1.1.10.x
#

if __name__ == "__main__":
    start_time = datetime.now()
    # snmp_get_all_data('192.168.111.29', 3)
    print(snmp_get_location('192.168.111.29'))
    for var in snmp_get_bulk('192.168.111.29', COMMUNITY, 'etherStatsEntry', 'RMON-MIB'):
        print(var)
    print(datetime.now() - start_time)
