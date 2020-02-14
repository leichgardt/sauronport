from pysnmp.hlapi import *

COMMUNITY = 'public'
OID = {'sysName': '1.3.6.1.2.1.1.5.0',  # hostname
       'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',  # ports status
       'ifSpeed': '1.3.6.1.2.1.2.2.1.5',  # ports speed
       'dot1dTpFdbAddress': '1.3.6.1.2.1.17.4.3.1.1',  # mac adress
       'dot1dTpFdbPort': '1.3.6.1.2.1.17.4.3.1.2',  # port
       'sysDescr': '1.3.6.1.2.1.1.1'}

ENGINE = SnmpEngine()  # 2.416 sec instead 4+


def snmp_get_next(ip, community, oid, mib='', engine=ENGINE):
    """
    SNMP request for a one parameter.
    MIB don't needed if use OID. But if use Object Name of OID then MID is needed to specify.
    Using v2c at mpModel=1. "mpMpdel=0" is a v1.
    Community is access level of request.
    """
    ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
    try:
        (errInd,
         errStat,
         errId,
         varBinds) = next(getCmd(engine,
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


def snmp_get_bulk(ip, community, oid, mib='', engine=ENGINE):
    """
    SNMP request returns a list of parameters.
    The same, MIB is needed only with ObjName.
    """
    rez = []
    ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
    try:
        for (errInd,
             errStat,
             errId,
             varT) in bulkCmd(engine,
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
    return obj[0].prettyPrint().split(split_by)[-1] if last else obj.prettyPrint().split(split_by)


def snmp_get_port_status(ip, port, community=COMMUNITY):
    """
    Getting a port status at router port x by OID 1.3.6.1.2.1.2.2.1.8.x
    Status: 1-up, 2-down, 3-testing, 4-unknown, 5-dormant, 6-notPresent, 7-lowerLayerDown.
    Using a function snmp_get_next::getCmd for pulling out a one parameter.
    """
    varBinds = snmp_get_next(ip, community, '1.3.6.1.2.1.2.2.1.8.' + str(port))
    if varBinds is not 0:
        rez = snmp_pretty(varBinds)
        if '1' in rez:
            return 'up'
        elif '2' in rez:
            return 'down'
        elif '3' in rez:
            return 'testing'
        elif '4' in rez:
            return 'unknown'
        elif '5' in rez:
            return 'dormant'
        elif '6' in rez:
            return 'notPresent'
        elif '7' in rez:
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
    """
    Getting a table with MACs and their ports with VLAN.
    ObjName: "dot1qTpFdbPort", MID: "Q-BRIDGE-MIB".
    Using a function snmp_get_next::getBulk for pulling out many parameters.
    """
    macs = []
    vlans = []
    varTable = snmp_get_bulk(ip, community, 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')
    if varTable is not 0:
        for varBinds in varTable:
            try:
                if int(varBinds[1]) == int(port):
                    varBind = snmp_pretty(varBinds[0], '.', False)
                    vlans.append(int(varBind[1]))
                    macs.append(str(varBind[2][1:-1]))
            except ValueError:
                continue
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


def snmp_get_errors(ip, port):
    """
    RX Frames:                  TX Frames:
        1 - CRC Error               1 - Excessive Deferral
        2 - Undersize               2 - CRC Error
        3 - Oversize                3 - Late Collision
        4 - Fragment                4 - Excessive Collision
        5 - Jabber                  5 - Single Collision
        6 - Drop Pkts               6 - Collision
        7 - Symbol Error
    """
    rx_frames = {'CRC': 0,
                 'Undersize': 0,
                 'Oversize': 0,
                 'Fragments': 0,
                 'Jabbers': 0,
                 'Drop': 0,
                 'Symbol': 0}
    tx_frames = {'Deferral': 0,
                 'CRC': 0,
                 'LateCol': 0,
                 'ExcessCol': 0,
                 'SingleCol': 0,
                 'Col': 0}
    varTable1 = snmp_get_bulk(ip, COMMUNITY, 'etherStatsEntry', 'RMON-MIB')
    varTable2 = snmp_get_bulk(ip, COMMUNITY, 'dot3StatsEntry', 'EtherLike-MIB')
    if varTable1 is not 0 and varTable2 is not 0:
        for varBinds in varTable1:
            varBind = snmp_pretty(varBinds, last=False)
            if '.' + str(port) in varBind[0][-4:]:
                if 'etherStatsCRCAlignErrors' in varBind[0]:
                    rx_frames['CRC'] = varBind[1]
                elif 'Undersize' in varBind[0]:
                    rx_frames['Undersize'] = varBind[1]
                elif 'Oversize' in varBind[0]:
                    rx_frames['Oversize'] = varBind[1]
                elif 'Fragments' in varBind[0]:
                    rx_frames['Fragments'] = varBind[1]
                elif 'Jabbers' in varBind[0]:
                    rx_frames['Jabbers'] = varBind[1]
                elif 'Drop' in varBind[0]:
                    rx_frames['Drop'] = varBind[1]
                elif 'Collisions' in varBind[0]:
                    tx_frames['Col'] = varBind[1]
        for varBinds in varTable2:
            varBind = snmp_pretty(varBinds, last=False)
            if '.' + str(port) in varBind[0][-4:]:
                if 'Single' in varBind[0]:
                    tx_frames['SingleCol'] = varBind[1]
                elif 'Deferred' in varBind[0]:
                    tx_frames['Deferral'] = varBind[1]
                elif 'Late' in varBind[0]:
                    tx_frames['LateCol'] = varBind[1]
                elif 'Excessive' in varBind[0]:
                    tx_frames['ExcessCol'] = varBind[1]
                elif 'Symbol' in varBind[0]:
                    rx_frames['Symbol'] = varBind[1]
        return rx_frames, tx_frames


def snmp_get_all_data(ip, port):
    sysname = snmp_get_sysname(ip)
    sysloc = snmp_get_location(ip)
    status = snmp_get_port_status(ip, port)
    speed = snmp_get_port_speed(ip, port)
    rx, tx = snmp_get_errors(ip, port)
    vlans, macs = snmp_get_port_mac(ip, port)
    return sysname, sysloc, status, speed, rx, tx, vlans, macs


def snmp_get_update(ip, port):
    status = snmp_get_port_status(ip, port)
    speed = snmp_get_port_speed(ip, port)
    vlans, macs = snmp_get_port_mac(ip, port)
    return status, speed, vlans, macs


if __name__ == "__main__":
    from datetime import datetime

    ip, port = '192.168.111.29', 3

    start_time = datetime.now()
    snmp_get_all_data(ip, port)
    print(datetime.now() - start_time)
