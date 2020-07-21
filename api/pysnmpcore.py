from pysnmp.hlapi import *


class PySNMPCore:

    """
    Класс для взаимодействия с маршрутизаторами через протокол SNMP.
    Содержит в себе несколько методов для одного главного, который посылает get/walk/set запрос по заданному OID/MIB.
    >>> PySNMPCore.snmp_cmd('get', ipaddress, 'ifAdminStatus', 'IF-MIB', attrib=port)
    """

    def __init__(self):
        self.__ENGINE = SnmpEngine()
        self.__CONTEXT_DATA = ContextData()
        self._COMMUNITY = 'public'
        self._COMMUNITY_DATA = CommunityData(self._COMMUNITY)

    def snmp_cmd(self, cmd, ip, obj, mib='', **kwargs):
        """
        Основной метод класса для отправки запросов SNMP.

        cmd:        get
                    walk
                    set

        obj:        может быть указан как OID (1.3.6.2.5...), так и через Object Name и MIB
        mib:        указывается, если запрос сформирован через ObjectName, а не через OID - Object IDentificator
        attrib:     атрибут запрашиваемого объекта
        value:      значение запрашиваемого объекта (используется для set)
        load:       булевая переменная загрузки дополнительных MIB
        private:    булевая переменная отправки приватного запроса
        """

        attrib = kwargs.get('attrib', None)
        value = kwargs.get('value', None)
        load = kwargs.get('load', False)
        private = kwargs.get('private', False)

        if mib is '':
            ObjId = ObjectIdentity(obj)
        elif attrib is None:
            ObjId = ObjectIdentity(mib, obj)
        else:
            ObjId = ObjectIdentity(mib, obj, attrib)

        ObjType = ObjectType(ObjId) if value is None else ObjectType(ObjId, value)

        if load:
            ObjId.addAsn1MibSource('file:///usr/share/snmp')  # 'http://mibs.snmplabs.com/asn1/@mib@'

        self._set_community('private') if private else self._set_community('public')

        if cmd is 'get':
            snmp_cmd = getCmd(self.__ENGINE,
                              self._COMMUNITY_DATA,
                              UdpTransportTarget((ip, 161), timeout=2.0, retries=1),
                              self.__CONTEXT_DATA,
                              ObjType)
        elif cmd is 'walk':
            snmp_cmd = bulkCmd(self.__ENGINE,
                               self._COMMUNITY_DATA,
                               UdpTransportTarget((ip, 161), timeout=2.0, retries=1),
                               self.__CONTEXT_DATA,
                               0, 25,  # nonRepeaters / maxRepetitions - MIB num are requesting
                               ObjType,
                               lexicographicMode=False)
        elif cmd is 'set':
            snmp_cmd = setCmd(self.__ENGINE,
                              self._COMMUNITY_DATA,
                              UdpTransportTarget((ip, 161), timeout=2.0, retries=1),
                              self.__CONTEXT_DATA,
                              ObjType)
        else:
            print('Invalid cmd given...')
            return -1

        try:
            if cmd is 'walk':
                rez = []
                for errInd, errStat, errId, varBinds in snmp_cmd:
                    if errInd or errStat or errId:
                        print(f'[snmp_{cmd}]:',
                              errInd if errInd else '',
                              f'{errStat.prettyPrint()} at {errId and varBinds[int(errId)]}' if errStat else '')
                        return -1
                    else:
                        for varBind in varBinds:
                            rez.append(varBind)
            else:
                errInd, errStat, errId, varBinds = next(snmp_cmd)
                if errInd or errStat or errId:
                    print(f'[snmp_{cmd}]:',
                          errInd if errInd else '',
                          f'{errStat.prettyPrint()} at {errId and varBinds[int(errId)]}' if errStat else '')
                    return -1
                else:
                    rez = varBinds
            if self._snmp_correct_oid(rez):
                return rez
            else:
                return -1
        except Exception as e:
            print(f"[snmp_{cmd}]: Exception:\n{e}\n")
            return -1

    def _set_community(self, comm):
        """метод для смены Community"""
        if self._COMMUNITY == comm:
            pass
        else:
            self._COMMUNITY = comm
            self._COMMUNITY_DATA = CommunityData(self._COMMUNITY)

    def _snmp_correct_oid(self, obj):
        """метод для проверки корректности OID: если результат запроса содержит сообщение об ошибке, то False"""
        try:
            if 'No Such Instance' in self._snmp_pretty(obj) or 'No Such Object' in self._snmp_pretty(obj):
                return False
            else:
                return True
        except TypeError:
            return True

    def _snmp_pretty(self, obj, split_by=' = ', last=True):
        """метод для формирования красивого вывода: вытягивание ответа из объекта запроса"""
        if isinstance(obj, str):
            return obj
        elif obj is -1:
            return -1
        else:
            if last:
                rez = obj[0].prettyPrint().split(split_by)[-1]
                if 'No Such Instance' in rez or 'No Such Object' in rez:
                    return -1
                else:
                    return rez
            else:
                return obj.prettyPrint().split(split_by)


if __name__ == '__main__':
    ip, port = '192.168.111.73', 5
    snmp = PySNMPCore()
    print(snmp.snmp_cmd('get', ip, 'ifAdminStatus', 'IF-MIB', attrib=port)[0])
