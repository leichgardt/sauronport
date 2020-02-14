from flask import Flask, request, render_template, send_from_directory
from snmp_update.ironpysnmp_class import IronSNMP
from logging import Formatter, INFO
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
snmp = IronSNMP()


@app.route('/')
def index(name=None):
    return render_template('index.html', name=name)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/api/update', methods=['GET'])
def post_request():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 'Invalid arguments', 400
            else:
                sysname, syslocation, sysuptime, status, speed, rx, tx, vlans, macs = snmp.get_all_data(ip, port)

                return {
                    "sysName": sysname,
                    "sysLocation": syslocation,
                    "sysUpTime": sysuptime,
                    "status": status,
                    "speed": speed,
                    "rxFrames": rx,
                    "txFrames": tx,
                    "vLan": vlans,
                    "mac": macs,
                }
    except Exception as e:
        print('post_request exception:', e)


@app.route('/api/update_auto', methods=['GET'])
def auto_request():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')

            status, speed, vlans, macs = snmp.get_update(ip, port)

            return {
                "status": status,
                "speed": speed,
                "vLan": vlans,
                "mac": macs
            }
    except Exception as e:
        print('auto_request exception:', e)


if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/errors.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d'))
    file_handler.setLevel(INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(INFO)
    app.logger.info('FlaSNMP')
    print('logger activated')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
