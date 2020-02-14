import pexpect
from functools import wraps


class IronPExpect:
    """docstring"""

    def __init__(self):
        self.ip = ''
        self.user = ''
        self.__password = ''
        self.pages = 1
        self.log = ''
        self.telnet = pexpect.spawn('ls')
        self.connected = False
        self.switchType = 0

    def _tn_auth(self):
        try:
            self.telnet = pexpect.spawn("telnet " + self.ip, timeout=2)
            self.switchType = self.telnet.expect(["User[Nn]ame:", "login:"])  # 0 - d-link, 1 - snr
            self.telnet.sendline(self.user)
            self.telnet.expect(["[Pp]ass[Ww]ord:"])
            self.telnet.sendline(self.__password)
            connectionResult = self.telnet.expect(["#", pexpect.TIMEOUT])
            if connectionResult == 0:
                print("Telnet Auth success")
                self.connected = True
                return True
            elif connectionResult == 1:
                print("Telnet connection refused")
                self.connected = False
                return False
        except Exception as e:
            print('Exception!', e)
            return False

    def logs(self, ip='', user='', password='', input_pages=1):
        self.ip = ip
        self.user = user
        self.__password = password
        self.pages = int(input_pages)

        if self._tn_auth():
            if self.switchType is 0:
                self.telnet.sendline("sh log")
                for _ in range(self.pages):
                    self.telnet.sendline("n")
                self.telnet.sendline("q")
                self.telnet.expect(["#", pexpect.TIMEOUT])
                self.log = self.telnet.before.decode('ascii')
                self.log = self.log.split('\n\r')
                for i, lane in enumerate(self.log):
                    if 'Next Entry' in lane:
                        self.log.pop(i)
                for i, lane in enumerate(self.log):
                    if 'Log Text' in lane:
                        self.log = self.log[i:]
                        break
                self.log = '\n'.join(self.log[:-1])
                self.telnet.close()
                return self.log
            elif self.switchType is 1:
                self.telnet.sendline('sh log buf lev warn')
                self.telnet.sendline('q')
                '1', self.telnet.expect(['#', pexpect.TIMEOUT])
                self.log = self.telnet.before.decode('ascii')

                start = self.log.find('SDRAM:') + 6
                end = start + self.log[start:].find('\n')
                log_count = int(self.log[start:end])
                log_range = (log_count - self.pages * 10, log_count + 1)

                self.telnet.sendline(f'sh log buf lev warn range {log_range[0]} {log_range[1]}')
                for _ in range(self.pages + 1):
                    self.telnet.send(' ')
                self.telnet.expect([pexpect.TIMEOUT, '#'])
                self.log = self.telnet.before.decode('ascii')

                self.log = self.log.split('\n')
                self.log = '\n'.join(self.log[1:-1])
                self.log = self.log.replace("<warnings>", "[warnings]")
                self.telnet.close()
                return self.log
            else:
                return "Logs are not available. Please, send report to administrator."

    def enable_rmon(self, ip='', user='', password=''):
        self.ip = ip
        self.user = user
        self.__password = password

        if self._tn_auth():
            if self.switchType is 0:
                self.telnet.sendline("enable rmon")
                self.telnet.expect(["Success", pexpect.TIMEOUT])
                self.telnet.sendline("save config")
                self.telnet.expect(["Success", pexpect.TIMEOUT])
                self.telnet.close()
                return self.telnet.before.decode('ascii')
            elif self.switchType is 1:
                self.telnet.sendline("config")
                self.telnet.sendline("rmon enable")
                self.telnet.sendline("exit")
                self.telnet.expect(["#", pexpect.TIMEOUT])
                self.telnet.sendline("write")
                self.telnet.expect([":", pexpect.TIMEOUT])
                self.telnet.sendline("Y")
                self.telnet.expect(["#", pexpect.TIMEOUT])
                self.telnet.close()
                return self.telnet.before.decode('ascii')
            else:
                return "Unknown switch"
        else:
            return -1

    def __del__(self):
        self.telnet.close()


if __name__ == '__main__':
    # ip = "192.168.110.87"
    ip = "192.168.110.71"
    user = "test"
    password = "123321"
    pages = 3

    tn = IronPExpect()
    print(tn.logs(ip, user, password, 1))

    # tn = pexpect.spawn('telnet ' + ip, timeout=0.2)
    # tn.sendline(user)
    # tn.sendline(password)
    # tn.expect(['#', pexpect.TIMEOUT])
