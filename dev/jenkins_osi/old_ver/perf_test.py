#!/usr/bin/python

import os
import re
import sys
import logging as log
import getopt
import json
import subprocess
import time
# import auto_rpls_kernel
# import device
import pnpapi
import json
from collections import OrderedDict


test_root = os.path.dirname(os.path.abspath(__file__))
device_root = test_root+ '/../pkt_server/dev_maintain/'
sys.path.append( device_root )



def console_out(logFilename):
    ''' Output log to file and console '''
    # Define a Handler and set a format which output to file
    log.basicConfig(
                    level    = log.DEBUG,
                    format   = '%(message)s',
                    datefmt  = '%Y-%m-%d %A %H:%M:%S',
                    filename = logFilename,
                    filemode = 'w')

    # Define a Handler and set a format which output to console
    console = log.StreamHandler()
    console.setLevel(log.INFO)
    formatter = log.Formatter('%(message)s')
    console.setFormatter(formatter)

"""
check the device:
    1 the status is idle
    2 the OS  and it's version. if the version is wrong, it should be update.
download the test kernel image and repalce it
start the test
waiting the test result
send the test report
"""



# prepare the test envirnoment by the platform
def reset_envirnonment( platform , board_info =None):
    return

#run the unit case
def run_unitcases(platform, board_info, domain, case_addr, run_cmd):
    if ( platform == '' ):
        log.error("please tell me what platform you want to test ")
        return -1

    report_file = test_root +'/' + domain +'_report.json'
    #test_report
    report = OrderedDict()
    detail_log = []
    report["domain_unit"] = domain
    report["platform"] = platform
    report["result"] = "unkonw"
    report["detail_log"]='now it is not support, we will support later'

    return result

def main(argv):
    console_out('logging.log')
    img_url = 'None'
    img_dir = 'None'
    test_plan = ''
    test_cycle = ''

    try:
        opts, args = getopt.getopt(argv,"hu:f:v:o:p:c:")
    except getopt.GetoptError:
        log.info("get the input parameter error ")
        sys.exit(2)

    for opt, arg in opts:
      if opt == '-h':
         log.info("\n\
            Please input the paramter, ep: \n\
            uint_test.py -u img_url -v d -p android \n\
            -u = test umage url \n\
            -f = test image file dir \n\
            -v = the hardware, platform-device-info(or hostname) \n\
            -o = the os version \n\
            -p = the test plan ID \n\
            -c = the test cycle name \n\
            -h : help")
         sys.exit()
      elif opt == "-u":
          img_url = arg
      elif opt == "-f":
          img_dir = arg
      elif opt == "-v":
          machines= eval(arg)
      elif opt == "-o":
           os_version = arg
      elif opt == "-p":
           test_plan = arg
      elif opt == "-c":
           test_cycle = arg
      else:
          log.info("unknow the input parameter")
          exit(1)

    """
    check the test machine status
    [\"clear-NUC-clrnuc03\",\"clear-NUC-clrnuc03\"]
    the machines name should same with its record in DB
    """
    clear_test_devices = []
    android_test_devices = []


    if machines == '':
        log.error("please input the device infomation")
        return -1
    else:
        for test_machine in machines:
            #check it statusi
            device_info = {}
            machine_info = device.get_info(test_machine)
            log.info(machine_info)
            if ( machine_info == "not found"):
                log.error(test_machine + " can't be tested, please check the devices, it does not register in the database ")
                return

            if ( machine_info.status != "idle"):
                log.error(test_machine + " can't be tested, please check the devices status ")
                return

            device_info["hostname"] = machine_info.hostname
            device_info["password"] = machine_info.password
            device_info["usrname"] = machine_info.usrname
            device_info["os_type"] = machine_info.os_type

            log.info(device_info)
            if device_info["os_type"] == "clear":
                clear_test_devices.append( device_info )

    log.info(clear_test_devices)

    # check if the test machine are the defaut test agent
    agents = pnpapi.pnp_getagent(test_plan)
    if ( clear_test_devices != [] ):
        for agent in agents:
            find = False
            for test_device in clear_test_devices:
                log.info( agent + "  " + test_device["hostname"] )
                if agent == test_device["hostname"]:
                    find = True
                    continue
            if find == False:
                log.error(" %s is not in the test machine list, please check" %agent)
                return

    """
    check the  os version
    for the performance test result tracking, we should make sure to use the same OS version
    replace the kernel
    """
    device_is_ready = True
    if (( img_url != 'None') and ( img_dir != 'None' )):
        log.error("eithor image url or image dir, not both.")
        return -1
    else:
        try:
            if ( clear_test_devices != []):
                for test_device in clear_test_devices:
                    # mark the device is busy
                    device_info = device.get_info(test_device["hostname"])
                    if ( device_info != "not found" ):
                        device_info.status = "busy"
                        device_info.save(force_update=True)
                    status = auto_rpls_kernel.set_clr_version(test_device["usrname"], test_device["hostname"], test_device["password"], os_version)
                    if status != 0:
                        device_is_ready = False
                        continue
                    status = auto_rpls_kernel.rpls_kernel(img_url, img_dir, test_device["usrname"], test_device["hostname"], test_device["password"], 22)
                    if status != 0:
                        device_is_ready = False
                        continue
            else:
                log.info( "we don't support this platform , if you think it should be support, please tell us!" )
                return -1
        except Exception as e:
            log.error("replace kernel error")
            log.error( e )

    if device_is_ready == True:
        #run default test case
        try:
            pnpapi.pnp_trigger(test_plan, test_cycle)
        except Exception as e:
            log.info("test error");
    # mark the device is busy
    if ( clear_test_devices != []):
        for test_device in clear_test_devices:
            device_info = device.get_info(test_device["hostname"])
            if ( device_info != "not found" ):
                device_info.status = "idle"
                device_info.save(force_update=True)

    return 0

if __name__ == '__main__':
      sys.exit(main(sys.argv[1:]))

