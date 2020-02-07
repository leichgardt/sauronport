$(document).ready(function() {

    var ip_element = document.getElementById('input_ip');
    var port_element = document.getElementById('input_port');
    var button = document.getElementById('start_button');
    var update_every = document.getElementById('update_every');
    var auto_updater;
    var pic = new Image(50, 50);

    function ValidateIP(ip) {
        return /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip)
    }
    function isNumeric(num){
      return !isNaN(num)
    }

    ip_element.oninput = function (event) {
        if (ValidateIP(ip_element.value) === true) {
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
            ip_element.classList.remove("is-invalid");
        } else {
            port_element.classList.add('is-invalid');
            ip_element.classList.remove("is-valid");
        }
    };

    function check_valid(ip_val, port_val) {
        return ValidateIP(ip_val) === true && isNumeric(port_val) === true;
    }

    button.onclick = function get_updates() {
        console.log('update!!!');
        if (check_valid(ip_element.value, port_element.value)) {
            update_data(ip_element.value, port_element.value);
            clearInterval(auto_updater);
            if (isNumeric(update_every.value)) {
                auto_updater = setInterval(update_auto, update_every.value * 1000, ip_element.value, port_element.value)
            }
        } else {
            set_danger_button(timeout=true)
        }
    };

    function set_danger_button(timeout=true) {
        button.disabled = true;
        button.classList.remove("btn-outline-primary");
        button.classList.add("btn-danger");
        if (timeout===true) {
            var timeout_button = setTimeout(restore_button, 1000);
        }
    }

    function restore_button() {
        button.disabled = false;
        button.classList.remove("btn-danger");
        button.classList.add("btn-outline-primary");
    }

    function data_up(data) {
        var today = new Date();
            var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
            var macs = JSON.parse(JSON.stringify(data["macs"]));
            var vlans = JSON.parse(JSON.stringify(data["vlans"]));

            if (data["status"] === "1-up") {
                pic.src = "/static/status-yes.jpg";
            } else if (data["status"] === "2-down") {
                pic.src = "/static/status-no.jpg";
            } else {
                pic.src = "/static/status-undef.jpg";
            }
            document.getElementById('img_status').src = pic.src;
            document.getElementById('status').innerHTML = time + "<br>" + JSON.parse(JSON.stringify(data["status"]));
            document.getElementById('speed').innerHTML = JSON.parse(JSON.stringify(data["speed"]));
            document.getElementById('addresses').innerHTML = '';
            for (let i = 0; i < macs.length; i++) {
                document.getElementById('addresses').innerHTML += macs[i] + ' VLAN:' + vlans[i] + '<br><br>';
            }
    }

    function update_data(ip_val, port_val) {
        var url = '/api/update?' + $.param({ip: ip_val, port: port_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                document.getElementById('ip_port').innerHTML = ip_val + ':' + port_val;
                document.getElementById('title').innerHTML = JSON.parse(JSON.stringify(data["descr"]));
                document.getElementById('sysname').innerHTML = JSON.parse(JSON.stringify(data["sysname"]));

                data_up(data);
            })
            .catch(error => console.log(error));
    }

    function update_auto(ip_val, port_val) {
        var url = '/api/update_auto?' + $.param({ip: ip_val, port: port_val});
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                data_up(data)
            })
            .catch(error => console.log(error));
    }
});