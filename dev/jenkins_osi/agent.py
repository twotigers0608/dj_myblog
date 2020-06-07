#!/usr/bin/python
import os
import json
import time
import signal
import select
import logging
import argparse
import traceback
import subprocess
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


WAIT_TIME = 60
TIMEOUT_RET = -8086


class Monitor(object):
    cpu_usage_threahold = 5
    cpu_temp_threshold = 40

    @classmethod
    def get_cpu_usage(cls):
        '''
        CPU usage: 0 - 100
        '''
        last_idle = last_total = 0
        usages = []
        for _ in range(10):
            with open('/proc/stat') as f:
                fields = [float(column)
                          for column in f.readline().strip().split()[1:]]
            idle, total = fields[3], sum(fields)
            idle_delta, total_delta = idle - last_idle, total - last_total
            last_idle, last_total = idle, total
            utilisation = 100.0 * (1.0 - idle_delta / total_delta)
            usages.append(utilisation)
            time.sleep(0.5)
        ret = sum(usages)/len(usages)
        logging.info('CPU Usage: %.2f%%' % ret)
        return ret

    @staticmethod
    def _cpu_thermal_files():
        thermal_dir = '/sys/class/thermal/'
        for d in os.listdir(thermal_dir):
            if d.startswith('thermal_zone'):
                type_file = os.path.join(thermal_dir, d, 'type')
                therm_type = open(type_file).read().strip()
                if therm_type == 'x86_pkg_temp':
                    yield os.path.join(thermal_dir, d, 'temp')

    @classmethod
    def get_cpu_temp(cls, sysfile_path):
        output = open(sysfile_path).read().strip()
        value = float(output)/1000
        logging.info('CPU Thermal: %.1f' % value)
        return value

    @classmethod
    def is_ok(cls):
        for temp_f in cls._cpu_thermal_files():
            if cls.get_cpu_temp(temp_f) > cls.cpu_temp_threshold:
                return False
        if cls.get_cpu_usage() > cls.cpu_usage_threahold:
            return False
        return True

    @classmethod
    def wait(cls):
        wait_count = 60
        while not cls.is_ok() and not is_exit:
            if wait_count == 0:
                logging.warn('Max wait count reached. Rebooting...')
                os.system('sudo reboot')
                time.sleep(1000)  # wait for reboot
                exit(-1)
            else:
                wait_count -= 1
                time.sleep(WAIT_TIME)


class REST(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _get_url(self, path):
        return self.base_url.rstrip('/') + path

    @staticmethod
    def _url_parse(url):
        ''' split url into (hostname, path)'''
        o = urlparse.urlparse(url)
        return o.netloc, o.path

    def _request(self, method, url, data=None):
        try:
            from httplib import HTTPConnection
        except ImportError:  # py3
            from http.client import HTTPConnection
        logging.info('request: %s %s' % (method, url))
        host, path = self._url_parse(url)
        conn = HTTPConnection(host)
        body = json.dumps(data) if data else None
        header = {'content-type': 'application/json'}
        conn.request(method, path, body, header)
        try:
            resp = conn.getresponse()
            buf = resp.read()
            return json.loads(buf.decode())
        except Exception:
            return {}
        finally:
            conn.close()

    def register(self):
        import socket

        hostname = socket.gethostname()
        machine_id = open('/etc/machine-id').read().strip()
        url = self._get_url('/agents')
        data = dict(hostname=hostname, machine_id=machine_id)
        logging.info('register agent: %s' % data)
        return self._request('POST', url, data)

    def get_next_job(self, agent_id):
        url = self._get_url('/agents/%s/jobs/next' % agent_id)
        return self._request('GET', url)

    def start_job(self, job_id):
        url = self._get_url('/jobs/%s/start' % job_id)
        return self._request('POST', url)

    def finish_job(self, job_id, ret_code, output):
        url = self._get_url('/jobs/%s/result' % job_id)
        data = dict(ret_code=ret_code, output=output)
        return self._request('POST', url, data)


def exec_job(job, timeout=0):
    cmd = job['cmd']
    current_env = os.environ.copy()
    current_env['DISPLAY'] = ':0'
    if job['env']:
        current_env.update(job['env'])
    try:
        logging.info('exec cmd: %s | env: %s' % (cmd, job['env']))
        p = subprocess.Popen(cmd, shell=True, bufsize=1,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, env=current_env,
                             universal_newlines=True)
        stdout = []
        poll = select.poll()
        poll.register(p.stdout)
        start_time = time.time()
        while timeout == 0 or time.time() - start_time < timeout:
            has_data = poll.poll(5)
            if has_data:
                line = p.stdout.readline()
                stdout.append(line)
                logging.debug(line.rstrip())
                if line == '' and p.poll() is not None:
                    break
        else:  # Timeout
            logging.error('running cmd TIMEOUT')
            p.kill()
            msg = ''.join(stdout) + '\n #### TIMEOUT %ss ####' % timeout
            return TIMEOUT_RET, msg
        return p.returncode, ''.join(stdout)
    except subprocess.CalledProcessError as e:
        logging.error(e.output)
        return (-1, e.output)


is_exit = False


def receive_signal(signum, stack):
    global is_exit
    print('Received:', signum)
    is_exit = True


signal.signal(signal.SIGTERM, receive_signal)
signal.signal(signal.SIGINT, receive_signal)


def main(url, nowait=False):
    if not nowait:
        logging.info('wait 60s before start')
        time.sleep(WAIT_TIME)
    # avoid stuck in phoronix asking for aggrement
    os.system('echo -e "y \n n \n" | phoronix-test-suite system-info')

    rest = REST(url)
    agent = rest.register()  # register agent
    agent_id = agent['id']
    logging.info('agent registered, id: %s' % agent_id)
    while not is_exit:  # job execution loop
        try:
            job = rest.get_next_job(agent_id)
            if not job:
                continue
            job_id = job['id']
            logging.info('received job (%s): %s' % (job['phase'], job['cmd']))
            if job['phase'] != 'Idle':
                if job['phase'] == 'Loop':  # wait system ready in real Loop
                    Monitor.wait()
                rest.start_job(job_id)
                ret_code, output = exec_job(job, job['timeout'])
                rest.finish_job(job_id, ret_code, output)
                # if ret_code == TIMEOUT_RET:
                #     logging.info('TIMEOUT: Reboot machine...')
                #     os.system('sudo reboot')
            else:  # Idle job
                if job['cmd']:
                    os.system(job['cmd'])
                else:
                    time.sleep(30)
            time.sleep(0.3)
        except Exception:  # just log error and continue
            logging.error(traceback.format_exc())
            time.sleep(3)  # wait 3s for error


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nowait', action='store_true', default=False,
                        help='Skip wait at startup (debug only)')
    parser.add_argument('--url', help='REST API base Url', required=True)
    args = parser.parse_args()
    # logging config
    FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    file_handler = logging.FileHandler(os.path.expanduser('~/agent.log'))
    file_handler.setFormatter(logging.Formatter(FORMAT))
    logging.getLogger().addHandler(file_handler)

    main(args.url, args.nowait)
