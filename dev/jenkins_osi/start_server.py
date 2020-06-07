import os
import paramiko
import sys
import argparse

def parse_args(arg_list):
    """osit runner arg parser"""
    parser = argparse.ArgumentParser(description="OS-independent test runner",
                                     epilog="Don't panic!")
    parser.add_argument("-H", dest="hostname", required=True,
                        action="store",
                        help="hostname: hostname or IP you need to connect")
    args = parser.parse_args(arg_list)
    return args

def main(arg_list):
    args = parse_args(arg_list)
    host = args.hostname
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port='22', username='pnp', password='')
    stdin, stdout, stderror = ssh.exec_command('python /home/pnp/agent.py --url http://10.238.158.184:5000/ --nowait')
    print(stdout.read())
    ssh.close()

if __name__ == "__main__":
    main(sys.argv[1:])

