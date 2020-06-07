import os
import sys
import re
import json
import time
import datetime
import logging
import requests
import argparse
from sshsession import SSHSession

REST_BASE = "http://10.238.158.184:5000/"
PROJECT = {'IKT_Project':'5ec4cc0babdb013dbb5ea8bf'}
TEST_PLAN = {'rt_perf':'5ec61343abdb01046f6a14c8','osit':'5ed5a90eabdb0179eec19fda'}
TGl_DEVICES = '5ecf1b979932a0692fd87378'
USER = 'pnp'
# START_AGENT = "echo 'python /home/pnp/agent.py --url http://10.238.158.184:5000/ --nowait' >> /devttyUSB1"
PATH = os.getcwd()

def parse_args(arg_list):
    """osit runner arg parser"""
    parser = argparse.ArgumentParser(description="OS-independent test runner",
                                     epilog="Don't panic!")
    parser.add_argument("-P", dest="plan",
                        action="store",
                        help="plan:plan to test name")
    parser.add_argument("-S", dest="staging", 
                        action="store",
                        help="staging: test cycles name")
    parser.add_argument("-H", dest="hostname", required=True,
                        action="store",
                        help="hostname: hostname or IP you need to connect")
    args = parser.parse_args(arg_list)
    return args


def get_projects(tgr_name):
    projects_url = REST_BASE + 'projrct_configs'
    resp = requests.get(projects_url, headers={
                        "Content-type": "application/json"}, verify=False)
    ret = resp.text
    if ret:
        results = json.loads(ret)
        for progect in results:
            if progect['projext']['name'] == tgr_name:
                projects_id = results['project']['id']
                break
    else:

        results = {}
    print(projects_id)
    return projects_id

def get_agent(host):
    get_devices = REST_BASE + 'agents/' + TGl_DEVICES
    resp = requests.get(get_devices, headers={"Content-type": "application/json"}, verify=False)
    agent_mess = json.loads(resp.text)
    try:
        os.popen('python3 ' + PATH + '/start_server.py -H ' + host)
    except:
        logging.info('longtime ssh shell')

def get_cycles(plan_id, cycles_name):
    cycles_url = REST_BASE + 'test_plans/' + plan_id + '/test_cycles'
    cycles = {'name': cycles_name, 'version_id' :cycles_name, 'plan_id': plan_id}
    cycles_js = json.dumps(cycles, indent=4)
    resp = requests.post(cycles_url, headers={"Content-type": "application/json"}, data=cycles_js, verify=False)
    ret = resp.text
    cycles_data = json.loads(ret)
    print(cycles_data)
    cycles_id = cycles_data['id']
    start_cycles = REST_BASE + 'test_cycles/' + cycles_id + '/actions'
    action_data = {"action": "start", "cycles_id":cycles_id}
    action_json = json.dumps(action_data, indent=4)
    resp = requests.post(start_cycles, headers={
                         "Content-type": "application/json"}, data=action_json, verify=False)
    if resp:
        print('start')
        return cycles_id
    else:
        requests.delete(REST_BASE + '/test_cycles/' + cycles_id)
        logging.info('test start fail,delete this job')

def check_cycles_status(cycles_id):
    while True:
        cycles_url = REST_BASE + 'test_cycles/'+ cycles_id + '/refresh'
        cycles_data = {'plan_id': plan_id}
        json_data = json.dumps(cycles_data)
        resp = requests.post(cycles_url, headers={"Content-type": "application/json"}, data=json_data, verify=False)
        ret = resp.text
        status = ret['status']
        if status == 'COMPLETED':
            return status
        else:
            time.sleep(60)

def main(arg_list):
    args = parse_args(arg_list)
    plan = args.plan
    host = args.hostname
    staging = args.staging
    for name,id in TEST_PLAN.items():
        if plan == name:
            plan_id = id
    ww = time.strftime("%W")
    cycles_name = 'ww_' + ww + '_' + staging
    print(plan_id)
    get_agent(host)
    cycles_id = get_cycles(plan_id, cycles_name)
    check_cycles_status(cycles_id)

if __name__ == "__main__":
    main(sys.argv[1:])
