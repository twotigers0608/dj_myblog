#!/usr/bin/env python
"""Author: Yifan Li
   Unittest of hostrunner
"""


import json
import logging
import os
import shutil
import unittest


import utils
import ssh_session


FORMAT = '%(asctime)-15s UNITTEST %(name)-10s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT,
                    level=logging.DEBUG)

test_logger = logging.getLogger(__name__)


class UtilsTest(unittest.TestCase):
    def test_format_asc_log_1(self):
        """test translate \'\\r\\n\' to \'\\n\'"""
        input_str = 'These violent delights have violent ends\r\nAnd in ' + \
                    'their triumph die,\r\nlike fire and powder.\r\n'
        output = 'These violent delights have violent ends\nAnd in their ' + \
                 'triumph die,\nlike fire and powder.\n'
        func_name = 'format_asc_log'
        fail_msg = "incorrect transfer from '\\r\\n' to '\\n."
        self.assertEqual(utils.format_asc_log(input_str), output,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_format_asc_log_2(self):
        """test translate \'\\n\\n\' to \'\\n\'"""
        input_str = 'Which as they kiss consume: the sweetest honey \n\nIs ' + \
                    'loathsome in his own deliciousness'
        output = 'Which as they kiss consume: the sweetest honey \nIs ' + \
                 'loathsome in his own deliciousness'
        func_name = 'format_asc_log'
        fail_msg = "incorrect translate from '\\n\\n' tp '\\n'"
        self.assertEqual(utils.format_asc_log(input_str), output,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_format_asc_log_3(self):
        """test translate \'"\' to \'\\\\\\\"\'"""
        input_str = 'And in the "taste" confounds the appetite:'
        output = 'And in the \\\"taste\\\" confounds the appetite:'
        func_name = 'format_asc_log'
        fail_msg = "incorrect translate from '\"' to '\\\"'"
        self.assertEqual(utils.format_asc_log(input_str), output,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_format_asc_log_4(self):
        """test translate \'\\x1b\' to \'\'"""
        input_str = 'Therefore\x1b love moderately;\x1b long love doth so;'
        output = 'Therefore love moderately; long love doth so;'
        func_name = 'format_asc_log'
        fail_msg = "incorrect translate from '\x1b' to ''"
        self.assertEqual(utils.format_asc_log(input_str), output,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_run_command_correct_input(self):
        """test run_command with correct input"""
        cmd = "echo HELLO; echo WORLD"
        expect_out = 'HELLO\nWORLD\n'
        cmd_out = utils.run_command(cmd)
        func_name = 'run_command'
        fail_msg = "incorrect output: %s, expected output: %s" %(cmd_out,
                                                                 expect_out)
        self.assertEqual(cmd_out, expect_out,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_run_command_get_return_code(self):
        """test get return code via run_command"""
        cmd = "sleep 2; echo $?"
        expect_out = '0\n'
        cmd_out = utils.run_command(cmd)
        func_name = 'run_command'
        fail_msg = "incorrect output: %s, expected output: %s" %(cmd_out,
                                                                 expect_out)
        self.assertEqual(cmd_out, expect_out,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_run_command_wrong_input(self):
        """test run_command with wrong input, also check return code"""
        cmd = "hahaha; echo $?"
        expect_out = '/bin/sh: 1: hahaha: not found\n127\n'
        cmd_out = utils.run_command(cmd)
        func_name = 'run_command'
        fail_msg = "incorrect output: %s, expected output: %s" %(cmd_out,
                                                                 expect_out)
        self.assertEqual(cmd_out, expect_out,
                         "Function: %s %s" %(func_name, fail_msg))


class StartSessionTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("test.json"):
            raise IOError("Test data: ./test.json not existed!")
        with open("test.json", "r") as test_fd:
            test_data = json.load(test_fd)
        self.test_data = test_data

    def test_create_session_with_domain(self):
        user, host, password = self.test_data["correct_session"]["user"], \
                               self.test_data["correct_session"]["host_domain"], \
                               self.test_data["correct_session"]["password"]
        test_session = ssh_session.SSHSession(user=user,
                                              host=host,
                                              password=password)
        func_name = "start_session_host_has_domain"
        fail_msg = "session create with host(has domain) should not be None!"
        self.assertIsInstance(test_session,
                              ssh_session.SSHSession,
                              "Function: %s %s" %(func_name, fail_msg))

    def test_create_correct_session(self):
        """check create session with correct data is expect instance"""
        user, host, password = self.test_data["correct_session"]["user"], \
                               self.test_data["correct_session"]["host"], \
                               self.test_data["correct_session"]["password"]
        test_session = ssh_session.SSHSession(user=user,
                                              host=host,
                                              password=password)
        func_name = "start_session"
        fail_msg = "session create with correct data should not be None!"
        self.assertIsInstance(test_session,
                              ssh_session.SSHSession,
                              "Function: %s %s" %(func_name, fail_msg))

    def test_create_session_without_password_raise_error(self):
        """check create session without password raise error"""
        user, host = self.test_data["correct_session"]["user"], \
                     self.test_data["correct_session"]["host"]
        func_name = "start_session"
        fail_msg = "incorrect error raised when no password input"
        with self.assertRaises(ssh_session.SSHConnectionError) as e:
            test_session = ssh_session.SSHSession(user=user,
                                                  host=host)
        self.assertEqual(e.exception.error_code, 1,
                         "Function: %s %s" %(func_name, fail_msg))

    def test_session_with_wrong_data_raise_error(self):
        """check create session with wrong data raise error"""
        user, host, password = self.test_data["wrong_session"]["user"], \
                               self.test_data["wrong_session"]["host"], \
                               self.test_data["wrong_session"]["password"]
        func_name = "start_session"
        fail_msg = "session with wrong data should raise SSHConnectionError!"
        with self.assertRaises(ssh_session.SSHConnectionError) as e:
            test_session = ssh_session.SSHSession(user=user,
                                                  host=host,
                                                  password=password)
        self.assertEqual(e.exception.error_code, 1,
                         "Function: %s %s" %(func_name, fail_msg))


class SessionMethodTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("test.json"):
            raise IOError("Test data: ./test.json not existed!")
        with open("test.json", "r") as test_fd:
            test_data = json.load(test_fd)
        self.test_data = test_data
        self.user, self.host = self.test_data["correct_session"]["user"], \
                               self.test_data["correct_session"]["host"]
        password = self.test_data["correct_session"]["password"]
        self.test_session = ssh_session.SSHSession(user=self.user,
                                                   host=self.host,
                                                   password=password)

    def test_get_command_output(self):
        """check command output correct or not"""
        output, _ = self.test_session.sendcommand(self.test_data["get_user"])
        func_name = "sendcommand"
        fail_msg = "incorrect output when session.send_command"
        self.assertEqual(output, [self.user],
                         "Function: %s %s" %(func_name, fail_msg))

    #TODO: Add check for send command get exception when timeout
    def test_command_timeout_raise_exception(self):
        """check command run into timeout will raise expect exception"""
        pass

    def test_check_hang_correct_input(self):
        """check check_hang function give correct input"""
        host_alive = self.test_session.check_hang(count=2)
        func_name = "check_hang"
        fail_msg = "incorrect result of check_hang, should be True"
        self.assertTrue(host_alive,
                        "Function: %s %s" %(func_name, fail_msg))

    def test_check_hang_wrong_input(self):
        """check check_hang function give correct input"""
        host_alive = self.test_session.check_hang(count=0)
        func_name = "check_hang"
        fail_msg = "incorrect result of check_hang, should be False"
        self.assertFalse(host_alive,
                         "Function: %s %s" %(func_name, fail_msg))


class SessionScpTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("test.json"):
            raise IOError("Test data: ./test.json not existed!")
        with open("test.json", "r") as test_fd:
            test_data = json.load(test_fd)
        self.test_data = test_data
        self.user, self.host = self.test_data["correct_session"]["user"], \
                               self.test_data["correct_session"]["host"]
        self.password = self.test_data["correct_session"]["password"]
        self.test_session = ssh_session.SSHSession(user=self.user,
                                                   host=self.host,
                                                   password=self.password)
        self.test_line = "We must know, we will know!"
        self.test_file_send = "toccata"
        self.test_file_get = "fuge"
        self.remote_directory = "/home/%s/session-scp-test-remote" %self.user
        self.local_directory = "~/sessison-scp-test-local"
        #create 
        os.makedirs(self.local_directory)
        self.test_session.sendcommand("mkdir -p %s" %self.remote_directory)

    def test_scp_send_to_remote(self):
        """test scp_send to remote"""
        #setup
        local_file_path = os.path.join(self.local_directory,
                                       self.test_file_send)
        remote_target_directory = os.path.join(self.remote_directory, '')
        with open(local_file_path, 'w') as fd:
            test_logger.info("Write '%s' to file %s.",
                             self.test_line,
                             local_file_path)
            fd.write(self.test_line)
        #send
        self.test_session.scp_send(local_file_path,
                                   remote_target_directory,
                                   self.password)
        #check result
        remote_file = os.path.join(remote_target_directory,
                                   self.test_file_send)
        o, _ = self.test_session.sendcommand("test -f %s; echo $?" %remote_file)
        func_name = "scp_send"
        fail_msg = "did not get file sent via scp_send!"
        self.assertIn("0", o,
                      "Function: %s %s" %(func_name, fail_msg))

    def test_scp_get_from_remote(self):
        """test scp_get from remote"""
        #setup
        remote_file_path = os.path.join(self.remote_directory,
                                       self.test_file_get)
        local_target_directory = os.path.join(self.local_directory, '')
        self.test_session.sendcommand("echo \"%s\" > %s" %(self.test_line,
                                                           remote_file_path))
        #test send
        self.test_session.scp_get(local_target_directory,
                                  remote_file_path,
                                  self.password)
        #check result
        local_file = os.path.join(local_target_directory, self.test_file_get)
        func_name = "scp_get"
        fail_msg = "did not get file sent via scp_get!"
        self.assertTrue(os.path.exists(local_file),
                        "Function: %s %s" %(func_name, fail_msg))

    #TODO: add test for recuresive mode
    def test_scp_send_to_remote_with_recursive(self):
        pass

    def test_scp_get_from_remote_with_recursive(self):
        pass

    def tearDown(self):
        self.test_session.sendcommand("rm -rf %s" %self.remote_directory)
        shutil.rmtree(self.local_directory)






if __name__ == "__main__":
    unittest.main(verbosity=2)
