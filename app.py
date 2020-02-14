__author__ = 'mamaragan'

from flask import Flask, request, render_template, redirect, url_for
from logging import Formatter, INFO
from logging.handlers import RotatingFileHandler
import os
from api.iron_pysnmp_class import IronSNMP
from api.iron_pexpect_class import IronPExpect
from api.config import *

app = Flask(__name__, static_folder='static')
snmp = [IronSNMP() for _ in range(3)]
telnet = IronPExpect()

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


@app.route('/')
def index():
    return render_template('index.html',
                           title='iMonit',
                           about=ABOUT,
                           version='0.4.0b Beta version',
                           main_url='http://cup.ironnet.info:5000',
                           libs=LIBS)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=200)


@app.route('/api/reload_port', methods=['GET'])
def reload_port():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            mode = request.args.get('mode', '')  # 1 - reload, 2 - disable
            print(mode)

            return {"answer": snmp[0].reload_port(ip, port, int(mode))}
    except Exception as e:
        print('[post_request_logs] exception:', e)


@app.route('/api/update_sys', methods=['GET'])
def post_request_sysdata():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            if len(ip) == 0:
                return 'Invalid arguments', 400
            else:
                sysname = snmp[0].get_sysname(ip)
                if sysname is -1 or sysname is 'timeout':
                    sysname, syslocation, sysuptime = 'n/a', 'n/a', 'n/a'
                else:
                    syslocation = snmp[0].get_syslocation(ip)
                    sysuptime = snmp[0].get_sysuptime(ip)
                return {
                    "sysName": sysname,
                    "sysLocation": syslocation,
                    "sysUpTime": sysuptime
                }
    except Exception as e:
        print('[post_request] exception:', e)


@app.route('/api/update_port', methods=['GET'])
def post_request_portdata():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 'Invalid arguments', 400
            else:
                status = snmp[1].get_port_status(ip, port)
                link = snmp[1].get_port_link(ip, port)
                if link is 'down':
                    speed, vlans, macs = '-', '-', '-'
                elif link is -1 or link is 'timeout':
                    speed, vlans, macs = 'n/a', 'n/a', 'n/a'
                else:
                    speed = snmp[1].get_port_speed(ip, port)
                    vlans, macs = snmp[1].get_port_mac(ip, port)
                return {
                    "status": status,
                    "link": link,
                    "speed": speed,
                    "vLan": vlans,
                    "mac": macs,
                }
    except Exception as e:
        print('[post_request] exception:', e)


@app.route('/api/update_err', methods=['GET'])
def post_request_porterrors():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 'Invalid arguments', 400
            else:
                rx, tx = snmp[2].get_errors(ip, port)

                return {
                    "rxFrames": rx,
                    "txFrames": tx
                }
    except Exception as e:
        print('[post_request] exception:', e)


@app.route('/api/update_auto', methods=['GET'])
def auto_request():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 'Invalid arguments', 400
            else:
                uptime = snmp[0].get_sysuptime(ip)
                status, link, speed, vlans, macs = snmp[1].get_update(ip, port)
                rx, tx = snmp[2].get_errors(ip, port)

                return {
                    "sysUpTime": uptime,
                    "status": status,
                    "link": link,
                    "speed": speed,
                    "vLan": vlans,
                    "mac": macs,
                    "rxFrames": rx,
                    "txFrames": tx
                }
    except Exception as e:
        print('[auto_request] exception:', e)


@app.route('/api/update_log', methods=['POST'])
def post_request_logs():
    try:
        if request.method == 'POST':
            json_data = request.get_json()
            ip = json_data.get('ip', '')
            login = json_data.get('login', '')
            # password = rsa.decode(json_data.get('password', ''))
            password = json_data.get('password', '')
            pages = json_data.get('pages', '')

            if len(ip) == 0 and len(login) == 0:
                return 'Invalid arguments', 400
            else:
                print(ip, login, password, pages)
                return {"logs": telnet.logs(ip, login, password, pages)}
    except Exception as e:
        print('[post_request_logs] exception:', e)


@app.route('/api/enable_rmon', methods=['POST'])
def post_request_enable_rmon():
    try:
        if request.method == 'POST':
            json_data = request.get_json()
            ip = json_data.get('ip', '')
            login = json_data.get('login', '')
            # password = rsa_decode(json_data.get('password', ''))
            password = json_data.get('password', '')

            return {"answer": telnet.enable_rmon(ip, login, password)}
    except Exception as e:
        print("[post_request_rsa] error", e)
