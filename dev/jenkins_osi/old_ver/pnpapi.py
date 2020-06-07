#!/usr/bin/env python3
import os
import sys
import re
import json
import time
import requests

REST_BASE="10.238.158.184:5000/"
def pnp_getagent(planid):
    url = REST_BASE + "test_plans/" + planid

    resp = requests.get(url, headers ={ "Content-type": "application/json" }, verify = False)
    ret = resp.text
    if ret:
        results = json.loads(ret)
    else:
        results = {}

    agents = []
    for agentsid in results["agents"]:
        url = REST_BASE + "agents/"+agentsid

        resp = requests.get(url, headers = { "Content-type": "application/json" }, verify = False)
        ret = resp.text
        if ret:
            results = json.loads(ret)
            agents.append(results["hostname"])
        else:
           results = {}
    print(agents)
    return agents

def pnp_trigger(planid, cycle_name):
    url = REST_BASE + "test_plans/"+planid +"/test_cycles"
    data={"name":cycle_name, "version_id":cycle_name}
    strbody = json.dumps(data, indent=4)
    resp = requests.post(url,  headers = { "Content-type": "application/json" }, data = strbody, verify = False)
    ret = resp.text
    print(ret)
    if ret:
        results = json.loads(ret)
        cycle_id = results["id"]
    else:
        results = {}
    print(cycle_id)

    url = REST_BASE + "test_cycles/" + cycle_id +"/actions"
    data = {"action": "start"}
    strbody = json.dumps(data, indent=4)
    resp = requests.post(url,  headers = { "Content-type": "application/json" }, data = strbody, verify = False)
    ret = resp.text
    print(ret)
    if ret:
        results = json.loads(ret)
    else:
        results = {}

    url = REST_BASE + "test_cycles/" + cycle_id

    while True:
        resp = requests.get(url, headers = { "Content-type": "application/json" }, verify = False)
        ret = resp.text
        if ret:
            results = json.loads(ret)
        else:
           results = {}
        if((results["status"] == "COMPLETED") or (results["status"] == "CANCELED")):
            print("this cycle is complete")
            return
        else:
            print("this cycle is busy")
            time.sleep(180)


def pnp_get(fields):
    url = REST_BASE + fields
    print(url)
    resp = requests.get(url, headers = { "Content-type": "application/json" }, verify = False)
    ret = resp.text
    print(ret)
    if ret:
        results = json.loads(ret)
    else:
        results = {}
    return results

def pnp_changeplan(planid, data):
    url = REST_BASE + "test_plans/"+planid
    resp = requests.get(url, headers = { "Content-type": "application/json" }, verify = False)
    ret = resp.text
    if ret:
        tmp_data = json.loads(ret)
    else:
        tmp_data = {}

    del tmp_data["id"]
    tmp_data["name"] = data
    print(tmp_data)
    resp = requests.put(url,  headers = { "Content-type": "application/json" }, data = tmp_data, verify = False)
    #ret = resp.text
    print(ret)
    if ret:
        results = json.loads(ret)
        cycle_id = results["id"]
    else:
        results = {}
    print(cycle_id)



def pnp_waitagent(agentsid):
    url = REST_BASE + "agents/"+agentsid

    while True:
        resp = requests.get(url, headers = { "Content-type": "application/json" }, verify = False)
        ret = resp.text
        if ret:
            results = json.loads(ret)
        else:
           results = {}
        if results["idle"] == False:
            print("this agents is busy")
            time.sleep(120)
        else:
            print("this agents is ready")
            return
    return


def main(argv):
    print(argv)
    fields = argv[1]
    if argv[0] == 'get':
        pnp_get(fields)
    elif argv[0] == 'pnp_waitagent':
        pnp_waitagent(fields)
    elif argv[0] == 'pnp_trigger':
        #1
        pnp_trigger(argv[1],argv[2])
    elif argv[0] == "pnp_getagent":
        pnp_getagent(argv[1])
    elif argv[0] == 'pnp_changeplan':
        pnp_changeplan(argv[1],argv[2])





if __name__ == '__main__':
     sys.exit(main(sys.argv[1:]))
