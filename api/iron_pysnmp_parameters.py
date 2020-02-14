errors_dict = (
    # RMON-MIB
    {'name': 'CRC Error',
     'OID': 'etherStatsCRCAlignErrors',
     'MIB': 'RMON-MIB'},
    {'name': 'Undersize',
     'OID': 'etherStatsUndersizePkts',
     'MIB': 'RMON-MIB'},
    {'name': 'Oversize',
     'OID': 'etherStatsOversizePkts',
     'MIB': 'RMON-MIB'},
    {'name': 'Fragments',
     'OID': 'etherStatsFragments',
     'MIB': 'RMON-MIB'},
    {'name': 'Jabbers',
     'OID': 'etherStatsJabbers',
     'MIB': 'RMON-MIB'},
    {'name': 'Drop Events',
     'OID': 'etherStatsDropEvents',
     'MIB': 'RMON-MIB'},

    # EtherLike-MIB
    {'name': 'Single Collision',
     'OID': 'dot3StatsSingleCollisionFrames',
     'MIB': 'EtherLike-MIB'},
    {'name': 'Excessive Deferral',
     'OID': 'dot3StatsDeferredTransmissions',
     'MIB': 'EtherLike-MIB'},
    {'name': 'Late Collision',
     'OID': 'dot3StatsLateCollisions',
     'MIB': 'EtherLike-MIB'},
    {'name': 'Excessive Collision',
     'OID': 'dot3StatsExcessiveCollisions',
     'MIB': 'EtherLike-MIB'},
    {'name': 'Symbol Error',
     'OID': 'dot3StatsSymbolErrors',
     'MIB': 'EtherLike-MIB'},
)

OID = {'sysName': '1.3.6.1.2.1.1.5.0',  # hostname
       'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',  # ports status
       'ifSpeed': '1.3.6.1.2.1.2.2.1.5',  # ports speed
       'dot1dTpFdbAddress': '1.3.6.1.2.1.17.4.3.1.1',  # mac adress
       'dot1dTpFdbPort': '1.3.6.1.2.1.17.4.3.1.2',  # port
       'sysDescr': '1.3.6.1.2.1.1.1'}

IP_BLACK_LIST = [
    '192.168.110.5', '192.168.110.106', '192.168.110.100', '192.168.110.200',
    '192.168.111.4', '192.168.111.6', '192.168.111.9', '192.168.111.12', '192.168.111.21', '192.168.111.29',
    '192.168.111.57', '192.168.111.103', '192.168.111.230', '192.168.111.249'
    '192.168.112.2', '192.168.112.3', '192.168.112.6'
    '192.168.113.3', '192.168.113.4', '192.168.113.5', '192.168.113.24', '192.168.113.65'
]
