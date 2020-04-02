#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'''
@desc Relay control
@history 2017-07-18: Yu Hai optimized based on relay card control code
'''
import sys
import time
import os
import logging
import serial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Relay_Card")

# key is hostname, value is port to control
HOST_CTL_MAP = {'bxt_gp-01-pk': 1,
                'bxt_gp_clr': 2,}
# relay control time
SLEEP_TIME = 0.05
# time for relay on_off action, the controled cables get connected in this time range
SHORT_TIME = 5

def check_relay_arg(number):
    ''' The input number must in 1 to 8 '''
    if 1 <= number <= 8:
        logger.info('Relay %d was chosen', number)
    else:
        logger.error('Relay number is from 1 to 8')
        sys.exit(1)

def get_dev_node():
    ''' Get serial usb node name of relay card '''
    ser_dev_dir = '/sys/bus/usb-serial/devices'
    for dev in os.listdir(ser_dev_dir):
        with open(os.path.join(ser_dev_dir, dev, 'uevent'), 'r') as fr:
            lines = fr.readlines()

        return dev if lines[0].startswith("DRIVER=cp210x\n") else None

def get_version(ser):
    ''' Relay software version '''
    cmd = 90
    logger.info("get the relay software version")
    ser.write(chr(cmd))
    time.sleep(SLEEP_TIME)
    text = ser.read(1)
    logger.info(ord(text))
    text = ser.read(1)
    logger.info(ord(text))
    time.sleep(1)

def set_relay_on(ser, num):
    ''' relay No. is from 1 to 8 '''
    cmd = 100 + num
    logger.info("set relay %d on ", num)
    ser.write(chr(cmd))
    logger.info("relay card status: %s", chr(cmd))
    time.sleep(SLEEP_TIME)
    ser.write(chr(91)) # get relay states
    text = ser.read(1)
    logger.info(ord(text))
    time.sleep(SLEEP_TIME)

def set_relay_off(ser, num):
    ''' relay No is from 1 to 8 '''
    cmd = 110 + num
    logger.info("set relay %d off", num)
    ser.write(chr(cmd))
    logger.info("relay card status: %s", chr(cmd))
    time.sleep(SLEEP_TIME)
    ser.write(chr(91))
    text = ser.read(1)
    logger.info(ord(text))
    time.sleep(SLEEP_TIME)

def set_relay_on_off(conn, num):
    ''' relay No is from 1 to 8 '''
    logger.info("set relay %d on-off", num)
    set_relay_on(conn, num)
    time.sleep(SHORT_TIME)
    set_relay_off(conn, num)
    time.sleep(SHORT_TIME)

def bxt_gp_power_on(hostname):
    ''' input hostname is a domain name '''
    port = HOST_CTL_MAP[hostname.split('.')[0]]
    try:
        ser = serial.Serial(os.path.join('/dev', get_dev_node()), 19200, serial.EIGHTBITS,
                            serial.PARITY_NONE, serial.STOPBITS_TWO, None)
        set_relay_on_off(ser, port)
        logger.info("Waiting for 30s to connect test board")
        time.sleep(30)

    except Exception as err:
        logger.error("Connection failed. It seems kernel issue which lead to board can't boot up or network can't work via ssh session. Please re-check kernel by manual test. %s", str(err))
