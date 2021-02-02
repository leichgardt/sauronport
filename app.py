__author__ = 'leichgardt'

import os
from flask import Flask, request, render_template, redirect, url_for
from logging import Formatter, INFO
from logging.handlers import RotatingFileHandler
from api.pysnmpapi import PySNMPApi
from api.pexpectapi import PExpectAPI
from api.config import Configer

app = Flask(__name__, static_folder='static')
snmp = [PySNMPApi() for _ in range(3)]
telnet = PExpectAPI()
host_domain = Configer().upload(module='Paladin')('domain')

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
    about = 'Приложение "SauronPort" предназначено для мониторинга портов и вытягивания логов коммутаторов.'
    return render_template('index.html',
                           title='SauronPort',
                           about=about,
                           version='0.4.0b Beta version',
                           main_url=host_domain + '/sauronport')


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

            return {"answer": snmp[0].reload_port(ip, port, int(mode))}
    except Exception as e:
        print('[post_request_logs] exception:', e)
        return -1


@app.route('/api/update_sys', methods=['GET'])
def post_request_sysdata():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            if len(ip) == 0:
                return 0
            else:
                sysname = snmp[0].get_sysname(ip)
                if sysname == -1 or sysname == 'timeout':
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
        return -1


@app.route('/api/update_port', methods=['GET'])
def post_request_portdata():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 0
            else:
                status = snmp[1].get_port_status(ip, port)
                link = snmp[1].get_port_link(ip, port)
                if link == 'down':
                    speed, vlans, macs = '-', '-', '-'
                elif link == -1 or link == 'timeout':
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
        return -1


@app.route('/api/update_err', methods=['GET'])
def post_request_porterrors():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 0
            else:
                rx, tx = snmp[2].get_errors(ip, port)

                return {
                    "rxFrames": rx,
                    "txFrames": tx
                }
    except Exception as e:
        print('[post_request] exception:', e)
        return -1


@app.route('/api/update_auto', methods=['GET'])
def auto_request():
    try:
        if request.method == 'GET':
            ip = request.args.get('ip', '')
            port = request.args.get('port', '')
            if len(ip) == 0 and len(port) == 0:
                return 0
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
        return -1


@app.route('/api/update_log', methods=['POST'])
def post_request_logs():
    try:
        if request.method == 'POST':
            json_data = request.get_json()
            ip = json_data.get('ip', '')
            login = json_data.get('login', '')
            password = json_data.get('password', '')
            pages = json_data.get('pages', '')

            if len(ip) == 0 and len(login) == 0:
                return 0
            else:
                if login == '':
                    return {"logs": telnet.logs(ip=ip, pages=int(pages))}
                else:
                    return {"logs": telnet.logs(ip=ip, user=login, password=password, pages=int(pages))}
    except Exception as e:
        print('[post_request_logs] exception:', e)
        return -1


@app.route('/api/enable_rmon', methods=['POST'])
def post_request_enable_rmon():
    try:
        if request.method == 'POST':
            json_data = request.get_json()
            ip = json_data.get('ip', '')
            login = json_data.get('login', '')
            password = json_data.get('password', '')

            return {"answer": telnet.enable_rmon(ip=ip, user=login, password=password)}
    except Exception as e:
        print("[post_request_rsa] error", e)
