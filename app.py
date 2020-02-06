from flask import Flask, request, render_template
from snmp_update.ironpysnmp import *
from datetime import datetime
import traceback

app = Flask(__name__)
# app.debug = False


@app.route('/')
def index(name=None):
    return render_template('index.html', name=name)


@app.route('/api/update', methods=['GET'])
def post_request():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 'Invalid arguments', 400
            else:
                # descr = '0'
                # sysname = '1'
                # status = '2'
                # speed = '3'
                # descr = snmp_get_sysdescr(ip)
                # sysname = snmp_get_sysname(ip)
                # status = snmp_get_port_status(ip, port, 'public')
                # speed = snmp_get_port_speed(ip, port, 'public')
                # macs = snmp_get_port_mac(ip, port, 'public')
                descr, sysname, status, speed, vlans, macs = snmp_get_all_data(ip, port)
                print(datetime.now().strftime("%H:%M:%S"), sysname, status, macs, vlans)

                return {
                    "ip": ip,
                    "port": port,
                    "sysname": sysname,
                    "descr": descr,
                    "status": status,
                    "speed": speed,
                    "vlans": vlans,
                    "macs": macs
                }
    except Exception as e:
        print('post_request exception:', e)


if __name__ == '__main__':
    app.run(load_dotenv=True)
