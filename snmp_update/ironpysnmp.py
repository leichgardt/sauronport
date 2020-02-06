from pysnmp.hlapi import *

OID = {'sysName': '1.3.6.1.2.1.1.5.0',  # hostname
       'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',  # ports status
       'ifSpeed': '1.3.6.1.2.1.2.2.1.5',  # ports speed
       'dot1dTpFdbAddress': '1.3.6.1.2.1.17.4.3.1.1',  # mac adress
       'dot1dTpFdbPort': '1.3.6.1.2.1.17.4.3.1.2',  # port
       'sysDescr': '1.3.6.1.2.1.1.1'}


def snmp_get_next(ip, comm, oid, mib=''):
    '''
    SNMP request for a one parameter.
    MIB don't needed if use OID. But if use Object Name of OID then MID is needed to specify.
    Using v2c at mpModel=1. "mpMpdel=0" is a v1.
    Community is access level of request.
    '''
    ObjId = ObjectIdentity(oid) if mib is '' else ObjectIdentity(mib, oid)
    try:
        errInd, errStat, errId, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(comm, mpModel=1),  # SNMPv2c
                   UdpTransportTarget((ip, 161), timeout=2.0, retries=0),
                   ContextData(),
                   ObjectType(ObjId)))
        if errInd or errStat:
            print('ERROR Ind/Stat from getCmd into snmp_get_next\n', errInd, errStat, errId)
            return None
        else:
            return varBinds
    except Exception as e:
        print("snmp_get_next: GetCmd exception:\n{0}\n".format(e))
        return None


def snmp_get_bulk(ip, comm, oid, mib=''):
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
                              CommunityData(comm, mpModel=1),
                              UdpTransportTarget((ip, 161), timeout=10.0, retries=5),
                              ContextData(),
                              0, 25,
                              ObjectType(ObjId),
                              lexicographicMode=False):
            if errInd or errStat:
                print('ERROR Ind/Stat from bulkCmd into snmp_get_bulk\n', errInd, errStat, errId)
                return None
            else:
                for varL in varT:
                    rez.append(varL)
                return rez
    except Exception as e:
        print("snmp_get_bulk: BulkCmd exception:\n{0}\n".format(e))
        return None


def snmp_get_port_status(ip, port, comm):
    '''
    Getting a port status at router port x by OID 1.3.6.1.2.1.2.2.1.8.x
    Status: 1-up, 2-down, 3-testing, 4-unknown, 5-dormant, 6-notPresent, 7-lowerLayerDown.
    Using a function snmp_get_next::getCmd for pulling out a one parameter.
    '''
    rez = None
    varBinds = snmp_get_next(ip, comm, '1.3.6.1.2.1.2.2.1.8.' + str(port))
    if varBinds is not None:
        rez = int(varBinds[0].prettyPrint().split(' = ')[1])
        if rez is 1:
            return '1-up'
        elif rez is 2:
            return '2-down'
        elif rez is 3:
            return '3-testing'
        elif rez is 4:
            return '4-unknown'
        elif rez is 5:
            return '5-dormant'
        elif rez is 6:
            return '6-notPresent'
        elif rez is 7:
            return '7-lowerLayerDown'
        else:
            return rez
    else:
        print('GET_PORT_STATUS: snmp_get_next error: the answer is empty.')


def snmp_get_port_speed(ip, port, comm):
    '''
    Getting a port speed at router port x by OID 1.3.6.1.2.1.2.2.1.5.x
    Answer shown as a bit/sec bandwidth, that's why output must be need to translated to Mbit/sec to readability.
    Using a function snmp_get_next::getCmd for pulling out a one parameter.
    '''
    varBind = snmp_get_next(ip, comm, '1.3.6.1.2.1.2.2.1.5.' + str(port))
    if varBind is not None:
        rez = str(varBind[0]).split('=')[-1].replace(' ', '')
        return str(int(rez) / 1000000) + ' Mbit/s'
    else:
        print('GET_PORT_SPEED: snmp_get_next error: the answer is empty.')


def snmp_get_port_mac(ip, port, comm):
    '''
    Getting a table with MACs and their ports with VLAN.
    ObjName: "dot1qTpFdbPort", MID: "Q-BRIDGE-MIB".
    Using a function snmp_get_next::getBulk for pulling out many parameters.
    '''
    macs = []
    vlans = []
    varTable = snmp_get_bulk(ip, comm, 'dot1qTpFdbPort', 'Q-BRIDGE-MIB')
    print('got varTable by snmp_get_bulk: varTable len =', len(varTable))
    if varTable is not None:
        for varBinds in varTable:
            print('reading:', varBinds)
            if int(varBinds[1]) == port:
                varBind = varBinds[0].prettyPrint().split('.')
                vlans.append(int(varBind[1]))
                macs.append(str(varBind[2][1:-1]))
        print('snmp_get_port_mac', vlans, macs)
        return vlans, macs
        # return (['123', '456'], ['789', '000'])
    else:
        print('GET_PORT_MAC: snmp_get_bulk error: the answer is empty.')
        return None


def snmp_get_sysdescr(ip):
    return snmp_get_bulk(ip, 'public', OID['sysDescr'])[0].prettyPrint().split(' = ')[1]


def snmp_get_sysname(ip):
    return snmp_get_next(ip, 'public', OID['sysName'])[0].prettyPrint().split(' = ')[1]


def snmp_get_all_data(ip, port):
    title = snmp_get_sysdescr(ip)
    sysname = snmp_get_sysname(ip)
    status = snmp_get_port_status(ip, port, 'public')
    speed = snmp_get_port_speed(ip, port, 'public')
    vlans, macs = snmp_get_port_mac(ip, port, 'public')
    vlan = ''
    if len(vlans) > 0:
        for i in vlans:
            vlan += str(i) + '//'
    mac = ''
    if len(macs) > 0:
        for i in macs:
            mac += str(i) + '//'
    return title, sysname, status, speed, vlan, mac