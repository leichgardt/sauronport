$(document).ready(function() {

    var ip_element = document.getElementById('input_ip');
    var port_element = document.getElementById('input_port');
    var button = document.getElementById('start_button');
    var update_every = document.getElementById('update_every');
    var auto_updater;
    var pic = new Image(50, 50);

    function validateIP(ip) {
        return /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip)
    }
    function isNumeric(num){
      return !isNaN(num)
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
        if (isNumeric(port_element.value) === true) {
            port_element.classList.add('is-valid');
            port_element.classList.remove("is-invalid");
        } else {
            port_element.classList.add('is-invalid');
            port_element.classList.remove("is-valid");
        }
    };

    function check_valid(ip_val, port_val) {
        return validateIP(ip_val) === true && isNumeric(port_val) === true;
    }

    button.onclick = function get_updates() {
        console.log('update!!!');
        clearInterval(auto_updater);
        if (button.classList.contains("btn-outline-success")) {
            restore_button();
        } else if (check_valid(ip_element.value, port_element.value)) {
            update_data(ip_element.value, port_element.value);
            if (isNumeric(update_every.value)) {
                auto_updater = setInterval(update_auto, update_every.value * 1000, ip_element.value, port_element.value);
                set_loading_button("Стоп");
            } else {
                set_loading_button("Ждите...");
            }
        } else {
            set_danger_button(timeout=true);
        }
    };

    function set_loading_button(btn_value) {
        button.classList.remove("btn-outline-primary");
        button.classList.add("btn-outline-success");
        button.value = btn_value;
    }

    function set_danger_button(timeout=true, timer=1000, btn_value="Ошибка") {
        button.value = btn_value;
        button.disabled = true;
        button.classList.remove("btn-outline-primary");
        button.classList.add("btn-danger");
        if (timeout===true) {
            var timeout_button = setTimeout(restore_button, timer);
        }
    }

    function restore_button() {
        button.disabled = false;
        button.value = "Запуск";
        button.classList.remove("btn-outline-success");
        button.classList.remove("btn-danger");
        button.classList.add("btn-outline-primary");
    }

    function restore_row(elementID, classes) {
        document.getElementById(elementID).classList.remove(classes)
    }

    function update_data(ip_val, port_val) {
        var url = '/api/update?' + $.param({ip: ip_val, port: port_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                document.getElementById('table_form').classList.remove('collapse');
                document.getElementById('ip_port').innerHTML = ip_val + ":" + port_val + " <a target=_blank href=\'http://" + ip_val + "/\'><i class=\'fa fa-external-link\'></i></a>";
                document.getElementById('title').innerHTML = JSON.parse(JSON.stringify(data["descr"]));
                document.getElementById('sysname').innerHTML = JSON.parse(JSON.stringify(data["sysname"]));

                fill_table(data);
            })
            .catch(error => {
                console.log(error);
                set_danger_button(true,2000);
            });
    }

    function fill_table(data) {
        if (button.value === "Ждите...") restore_button();
        var today = new Date();
        var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
        var macs = JSON.parse(JSON.stringify(data["macs"]));
        var vlans = JSON.parse(JSON.stringify(data["vlans"]));

        document.getElementById('status_row').classList.add("text-warning");
        var timeout_status = setTimeout(restore_row, 500, 'status_row', 'text-warning');

        document.getElementById('status').innerHTML = "(<i class='fa fa-clock-o'></i> " + time + ") — " + JSON.parse(JSON.stringify(data["status"]));
        document.getElementById('speed').innerHTML = JSON.parse(JSON.stringify(data["speed"]));
        document.getElementById('addresses').innerHTML = '';
        for (let i = 0; i < macs.length; i++) {
            document.getElementById('addresses').innerHTML += macs[i] + ' VLAN:' + vlans[i] + '<br>';
        }
    }

    function update_auto(ip_val, port_val) {
        var url = '/api/update_auto?' + $.param({ip: ip_val, port: port_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                fill_table(data)
            })
            .catch(error => {
                console.log(error);
                set_danger_button(true, 2000, "Ошибка автообновления");
                clearInterval(auto_updater);
            });
    }
});