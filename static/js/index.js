$(document).ready(function() {
    let ip_element = document.getElementById('input-ip'),
        port_element = document.getElementById('input-port'),
        login_element = document.getElementById('input-login'),
        password_element = document.getElementById('input-password'),
        pages_element = document.getElementById('input-pages');

    let btn, btn_value, btn_spinner,
        start_button = document.getElementById('start-button'),
        start_button_value = document.getElementById('button-value');
    let start_button_spinner = document.getElementById('button-spinner'),
        enable_port_button = document.getElementById('enable-port-button'),
        disable_port_button = document.getElementById('disable-port-button');
    let logs_button = document.getElementById('logs-button'),
        logs_button_value = document.getElementById('logs-button-value'),
        logs_button_spinner = document.getElementById('logs-button-spinner');
    let enable_rmon_button = document.getElementById('enable-rmon-button'),
        modal_logs_button = document.getElementById('modal-logs-button'),
        login_button = document.getElementById('login-button'),
        close_login_modal_button = document.getElementById('close-login-modal-button');

    let update_every = document.getElementById('update-every'),
        auto_updater, request_timer,
        loading_queue = 0;

    let modal_button = document.getElementById('reload-modal-button'),
        port_modal_label = document.getElementById('reload-modal-label'),
        port_modal_body = document.getElementById('reload-modal-body');

    function loading_status() {
        // nullifies when auto-update is off
        loading_queue += 1;

        if (!isNumeric(update_every.value) &&
            loading_queue >= 3) {
            button_status('default');
            loading_queue = 0;
        }
    }

    function button_status(bStatus='default', bButton='start', bValue='') {
        // Statuses: default, loading, error
        // Buttons: start, logs
        if (bButton === 'start') {
            btn = start_button;
            btn_value = start_button_value;
            btn_spinner = start_button_spinner;
        } else if (bButton === 'logs') {
            btn = logs_button;
            btn_value = logs_button_value;
            btn_spinner = logs_button_spinner;
        }
        if (bStatus === 'default') {
            if (bValue === '') btn_value.innerHTML = "Запуск";
            else btn_value.innerHTML = bValue;
            btn_value.classList.add('show');
            btn_spinner.classList.remove('show');
            btn.disabled = false;
            btn.classList.add("btn-outline-primary");
            btn.classList.remove("btn-outline-success", "btn-danger");
        }
        else if (bStatus === 'loading') {
            if (bValue === '') btn_value.classList.remove('show');
            else {
                btn_value.innerHTML = bValue;
                btn_value.classList.add('show');
            }
            btn_spinner.classList.add('show');
            btn.classList.add("btn-outline-success");
            btn.classList.remove("btn-outline-primary", "btn-danger");
        }
        else if (bStatus === 'error') {
            if (bValue === '') btn_value.innerHTML = 'Ошибка';
            else btn_value.innerHTML = bValue;
            btn_value.classList.add('show');
            btn_spinner.classList.remove('show');
            btn.disabled = true;
            btn.classList.add("btn-danger");
            btn.classList.remove("btn-outline-primary", "btn-outline-success");
            if (bButton === 'start')
                setTimeout(button_status, 1500, 'default', 'start');
            else if (bButton === 'logs')
                setTimeout(button_status, 1500, 'default', 'logs', 'Выгрузить логи');
            loading_queue = 0;
        }
    }

    // Validation
    function validateIP(ip) {
        return /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip)
    }
    function isNumeric(num){
      return !isNaN(num)
    }
    function check_valid(ip_val, port_val) {
        return validateIP(ip_val) === true && isNumeric(port_val) === true;
    }

    ip_element.oninput = function (event) {
        if (validateIP(ip_element.value) === true) {
            ip_element.classList.add('is-valid');
            ip_element.classList.remove("is-invalid");
        } else {
            ip_element.classList.add('is-invalid');
            ip_element.classList.remove("is-valid");
        }
    };

    port_element.oninput = function (event) {
        if ((isNumeric(port_element.value) === true) && (port_element.value !== '')) {
            port_element.classList.add('is-valid');
            port_element.classList.remove("is-invalid");
        } else {
            port_element.classList.add('is-invalid');
            port_element.classList.remove("is-valid");
        }
    };

    // Enter-click handler
    ip_element.onkeyup = function (event) {
        if (event.which === 13 || event.keyCode === 13) {
            start_button.click();
        }
    };
    port_element.onkeyup = function (event) {
        if (event.which === 13 || event.keyCode === 13) {
            start_button.click();
        }
    };

    start_button.onclick = function get_updates() {
        console.log("Button clicked");

        clearInterval(auto_updater); // auto updater clears and resets every button click
        clearTimeout(request_timer); // timeout timer from latest request clears too

        if (start_button.classList.contains("btn-outline-success")) {
            button_status('default');
        } else if (check_valid(ip_element.value, port_element.value)) {

            update_data_sys(ip_element.value, port_element.value);
            update_data_port(ip_element.value, port_element.value);
            update_port_errors(ip_element.value, port_element.value);
            button_status("loading");

            if (isNumeric(update_every.value)) {
                auto_updater = setInterval(update_auto, update_every.value * 1000,
                    ip_element.value, port_element.value);
            } else {
                request_timer = setTimeout(button_status, 10000,
                    "error", "Timeout");
            }
        } else {
            button_status("error");
        }
    };

    enable_port_button.onclick = function () {
        reload_port(ip_element.value, port_element.value, 1);
    };

    disable_port_button.onclick = function () {
        reload_port(ip_element.value, port_element.value, 2);
    };

    function reload_port(ip_val, port_val, mode) {
        let url = 'api/reload_port?' + $.param({ip: ip_val, port: port_val, mode: mode});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data['answer'] === -1) {
                    port_modal_label.innerText = "Ошибка";
                    port_modal_body.innerText = "Управление данным портом или маршрутизатором запрещено.";
                    modal_button.click();
                } else {
                    start_button.click();
                }
            })
            .catch(error => {
                console.log("[reload_port]", error);
            });
    }

    function restore_row(elementID, classes) {
        // intended for delete 'text-warning' class from 'data-port-status' line at table
        document.getElementById(elementID).classList.remove(classes);
    }

    function update_data_sys(ip_val, port_val) {
        let url = 'api/update_sys?' + $.param({ip: ip_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                clearTimeout(request_timer);
                loading_status();

                console.log("[SNMP] sys_data:", data);
                fill_table_sys(data, ip_val, port_val)
            })
            .catch(error => {
                console.log("[update_data_sys]", error);
                button_status("error");
                clearInterval(auto_updater);
                hide_sys_table();
            });
    }

    function fill_table_sys(data, ip_val, port_val) {
        document.getElementsByName('sys-table').forEach(function (element){
            element.classList.add('show');
        });
        document.getElementById('table-form').classList.add('show');

        document.getElementById('ip-port').innerHTML = ip_val + ":" + port_val + " <a target=_blank href=\'http://" + ip_val + "/\'><i class=\'fa fa-external-link\'></i></a>";
        document.getElementById('sysname').innerHTML = JSON.parse(JSON.stringify(data["sysName"]));
        document.getElementById('syslocation').innerHTML = JSON.parse(JSON.stringify(data["sysLocation"]));
        document.getElementById('sysuptime').innerHTML = JSON.parse(JSON.stringify(data["sysUpTime"]));
    }

    function hide_sys_table() {
        document.getElementsByName('sys-table').forEach(function (element){
            element.classList.remove('show');
        });
    }

    function update_data_port(ip_val, port_val) {
        let url = 'api/update_port?' + $.param({ip: ip_val, port: port_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                clearTimeout(request_timer);
                loading_status();

                console.log("[SNMP] port data received");

                fill_table_port(data);
            })
            .catch(error => {
                console.log("[update_data_port]", error);
                button_status("error");
                clearInterval(auto_updater);
                hide_port_table();
            });
    }

    function fill_table_port(data) {
        document.getElementsByName('port-table').forEach(function (element){
            element.classList.add('show');
        });
        document.getElementById('table-form').classList.add('show');
        let macs = JSON.parse(JSON.stringify(data["mac"]));
        let vlans = JSON.parse(JSON.stringify(data["vLan"]));

        document.getElementById('status-row').classList.add("text-warning");
        setTimeout(restore_row, 500, 'status-row', 'text-warning');
        if (data["status"] === 1) {
            document.getElementById('status').innerHTML = 'Включен';
        } else if (data["status"] === 2) {
            document.getElementById('status').innerHTML = 'Выключен';
        } else {
            document.getElementById('status').innerHTML = JSON.parse(JSON.stringify(data["status"]));
        }

        document.getElementById('link').innerHTML = JSON.parse(JSON.stringify(data["link"])) + " (" +
            JSON.parse(JSON.stringify(data["speed"])) + ")";
        document.getElementById('mac').innerHTML = '';
        document.getElementById('vlan').innerHTML = '';

        for (let i = 0; i < macs.length; i++) {
            document.getElementById('mac').innerHTML += macs[i] + '<br>';
            document.getElementById('vlan').innerHTML += vlans[i] + '<br>';
        }
    }

    function hide_port_table() {
        document.getElementsByName('port-table').forEach(function (element){
            element.classList.remove('show');
        });
    }

    function update_port_errors(ip_val, port_val) {
        let url = 'api/update_err?' + $.param({ip: ip_val, port: port_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                clearTimeout(request_timer);
                loading_status();

                console.log("[SNMP] port_errors:", data);
                fill_table_errors(data)
            })
            .catch(error => {
                console.log("[update_port_errors]", error);
                button_status("error");
                clearInterval(auto_updater);
                hide_errors_table();
            });
    }

    function fill_table_errors(data) {
        document.getElementsByName('errors-table').forEach(function (element){
            element.classList.add('show');
        });
        document.getElementById('table-form').classList.add('show');

        document.getElementById('errors1').innerHTML = '';
        document.getElementById('errors2').innerHTML = '';
        document.getElementById('errors3').innerHTML = '';
        document.getElementById('errors4').innerHTML = '';

        Object.keys(data['rxFrames']).forEach(function (key) {
            document.getElementById('errors1').innerHTML += key + "<br>";
            if ((data['rxFrames'][key] === '') || (data['rxFrames'][key] === -1))
                document.getElementById('errors2').innerHTML += "n/a<br>";
            else
                document.getElementById('errors2').innerHTML += data['rxFrames'][key] + "<br>";
        });
        Object.keys(data['txFrames']).forEach(function (key) {
            document.getElementById('errors3').innerHTML += key + "<br>";
            if ((data['txFrames'][key] === '') || (data['txFrames'][key] === -1))
                document.getElementById('errors4').innerHTML += "n/a<br>";
            else
                document.getElementById('errors4').innerHTML += data['txFrames'][key] + "<br>";
        });
    }

    function hide_errors_table() {
        document.getElementsByName('errors-table').forEach(function (element){
            element.classList.remove('show');
        });
    }

    function update_auto(ip_val, port_val) {
        button_status("loading");
        update_data_sys(ip_val, port_val);
        update_data_port(ip_val, port_val);
        update_port_errors(ip_val, port_val);
    }

    function auth_valid() {
        return !(login_element.value === '' || ip_element.value === '' || pages_element.value === '' || pages_element.value === '0')
    }

    logs_button.onclick = function get_logs() {
        console.log("Logs button clicked");
        button_status('loading', 'logs');
        update_logs(ip_element.value, '', '', pages_element.value);
        // update_logs(ip_element.value, login_element.value, password_element.value, pages_element.value);
    };

    modal_logs_button.onclick = function get_auth_logs() {
        if (auth_valid()) {
            console.log("Authorization and log pulling");
            button_status('loading', 'logs');
            update_logs(ip_element.value, login_element.value, password_element.value, pages_element.value);
        } else {
            button_status('error', 'logs');
            login_element.classList.add('is-invalid');
        }
        close_login_modal_button.click();
    }

    login_element.oninput = function (event) {
        if (login_element.value !== '') {
            login_element.classList.add('is-valid');
            login_element.classList.remove("is-invalid");
        } else {
            login_element.classList.add('is-invalid');
            login_element.classList.remove("is-valid");
        }
    };

    // Enter-key handler
    login_element.onkeyup = function (event) {
        if (event.which === 13 || event.keyCode === 13) {
            modal_logs_button.click();
        }
    };

    password_element.onkeyup = function (event) {
        if (event.which === 13 || event.keyCode === 13) {
            modal_logs_button.click();
        }
    };

    pages_element.onkeyup = function (event) {
        if (event.which === 13 || event.keyCode === 13) {
            logs_button.click();
        }
    };

    function update_logs(ip_val, login_val, password_val, pages_val) {
        let url = 'api/update_log';
        let data = {'ip': ip_val, 'login': login_val, 'password': password_val, 'pages': pages_val};
        fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                console.log("Got logs");
                if (data["logs"] === null) {
                    button_status("error", "logs", "Ошибка");
                    login_button.click();
                } else {
                    button_status("default", "logs", "Выгрузить логи");
                    data["logs"] = data["logs"].replace(/--More--/, '');
                    data["logs"] = data["logs"].replace(new RegExp('\b', 'g'), '');
                    document.getElementsByName('logs-table').forEach(function (element) {
                        element.classList.add('show');
                    });
                    document.getElementById('table-form').classList.add('show');
                    document.getElementById('logs').innerHTML = JSON.parse(JSON.stringify(data["logs"]));
                }
            })
            .catch(error => {
                console.log("[update_logs]", error);
                button_status("error", "logs");
                login_button.click();
            });
    }

    enable_rmon_button.onclick = function enable_rmon() {
        console.log("Enabling RMON...");
        if (auth_valid()) {
            // button_status('loading', 'logs_drop');
            update_enable_rmon(ip_element.value, login_element.value, password_element.value);
        }
        else {
            // button_status('error', 'logs_drop');
        }
    };

    function update_enable_rmon(ip_val, login_val, password_val) {
        let url = 'api/enable_rmon';
        let data = {'ip': ip_val, 'login': login_val, 'password': password_val};
        fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data['answer'] === -1) {
                    console.log("RMON error:", data);
                    port_modal_label.innerText = 'Ошибка';
                    port_modal_body.innerText = 'Неправильно введен логин или пароль.';
                    modal_button.click();
                } else {
                    console.log("RMON enabled:", data);
                    setTimeout(start_button.click, 250);
                }
            })
            .catch(error => {
                console.log("[enable_rmon]", error);
            });
    }
});
