from flask import Flask, request, render_template
from snmp_update.ironpysnmp import *

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
                descr, sysname, status, speed, vlans, macs = snmp_get_all_data(ip, port)

                return {
                    "sysname": sysname,
                    "descr": descr,
                    "status": status,
                    "speed": speed,
                    "vlans": vlans,
                    "macs": macs
                }
    except Exception as e:
        print('post_request exception:', e)


@app.route('/api/update_auto', methods=['GET'])
def auto_request():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')

            status, speed, vlans, macs = snmp_get_update(ip, port)

            return {
                "status": status,
                "speed": speed,
                "vlans": vlans,
                "macs": macs
            }
    except Exception as e:
        print('auto_request exception:', e)


if __name__ == '__main__':
    app.run(load_dotenv=True)
