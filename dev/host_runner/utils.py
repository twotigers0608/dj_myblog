#!/usr/bin/env python
"""Author: Yifan Li
   Utils function library
"""

import logging
import subprocess

###LOGGER###
logger = logging.getLogger("Utils")
logger.setLevel(logging.INFO)


def format_asc_log(new_line):
    """Change ascii format output to python str format line"""
    replacements = {
        '\n\n': '\n',  # double lines to single
        '\r': '',  # change \r\n to \n
        '"': '\\\"',  # escape double quotes for YAML syntax
        '\x1b': ''  # remove escape control characters
    }
    logger.debug("Format input: %s", new_line)
    for key, value in replacements.items():
        new_line = new_line.replace(key, value)
    return new_line

def run_command(command):
    """Run command with subprocess"""
    logger.debug("Run command: %s", command)
    try:
        cmd_out = subprocess.check_output(command,
                                          shell=True,
                                          stderr=subprocess.STDOUT)
        cmd_out = cmd_out.decode('utf-8')
    except subprocess.CalledProcessError as e:
        cmd_out = e.output.decode('utf-8')
        logger.error("Error found when running cmd %s, output is %s \
                      with return code %s", command, cmd_out, e.returncode)
    logger.info("Output: %s", cmd_out)
    return cmd_out
