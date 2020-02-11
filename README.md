# FlaSNMP
Port Monitoring on Switch with Flask and pysnmp into WEB-app.

### Todo list
 - ~~PySNMP requests~~
 - ~~Table HTML output~~
 - ~~Dynamic update~~
 - ~~Bootstrap.js style~~
 - ~~Cancel button of update~~
 - ~~Auto errors logging~~
 - ~~Info-widgets~~
 - ~~Timeout handler for requests~~
 - More readable port status output
 - Errors on port
 - js syntax error handler
 - Output data (addresses) from DB by `%switch_name` (`sw29`)
 - Rework the `dtable.js`
 - Improve HTML table
 - Write tests


### Installation
```sh
$ git clone git@github.com:mamaragan/FlaSNMP.git
$ cd FlaSNMP
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Starting
```sh
$ python app.py
```
