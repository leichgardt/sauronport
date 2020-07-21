# SauronPort
Port Monitoring on Switches with Flask and pysnmp into WEB-app (python-flask-uwsgi).

### Installation
Install dependencies
```sh
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt-get install liblzma-dev lzma
$ sudo apt-get install libpcre3 libpcre3-dev python3.8 python3.8-dev
```
And then clone the project
```
$ git clone git@github.com:leichgardt/sauronport.git
$ cd billeach
$ python3.8 -m venv venv
$ source venv/bin/activate
```

### Starting
If everything was done correctly, check it by running flask
```sh
$ flask run
```
uWSGI runs by script (without venv are possible)
```sh
$ uwsgi --ini uwsgi.ini
```