from flask import Flask, request, render_template, send_from_directory
from snmp_update.ironpysnmp import *
import logging
from logging.handlers import RotatingFileHandler
import os
# import sentry_sdk
#
# sentry_sdk.init("https://537ea3f5cb234b229a38792b15809a0f@sentry.io/2403315")
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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/errors.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('FlaSNMP')
    print('logger activated')

if __name__ == '__main__':
    print("main case :: :: ::")
    app.run(host='0.0.0.0', load_dotenv=True, debug=True)
