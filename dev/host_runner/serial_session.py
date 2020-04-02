#!/usr/bin/env python
"""Author: Yifan Li
   Serial Session module, include SerialSession
"""

import codecs
import logging
import serial
import threading

from utils import format_asc_log

class SerialConnectionError(Exception):
    """ Serial connection failed error"""
    error_code = 1
    error_help = "Serial connection error"
    error_type = "Connection"

class LogBuffer():
    """buffer of logs got from serial console, str"""
    def __init__(self):
        self.name = "LogBuffer"
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self._buffer = ""

    def write(self, text):
        self._buffer += text

    def flush_raw(self):
        """flush as return"""
        output = self._buffer
        self._buffer = ""
        return output

    def flush_to_file(self, file_path):
        """flush bufferred logs to file descriptor"""
        with open(file_path, "a") as fd:
            fd.write(self._buffer)
            self.logger.info("Buffer wrote to file %s, len %d.",
                              file_path,
                              len(self._buffer))
            self._buffer = ""
        return

class SerialSession():
    """Serial session class"""
    #TODO: Add context manager here
    def __init__(self, port, baudrate=115200, timeout=10):
        """timeout is for read function"""
        self.name = "SerialSession"
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.port = port
        self.baudrate = baudrate
        self.read_timeout = timeout
        self.session_alive = False
        self._reader_alive = False
        self.receiver_thread = None
        self.log_buffer = None
        self.input_encoding = None
        self.rx_decoder = None
        self.session = self._start_session()
        if not self.session:
            raise SerialConnectionError("Session not established!")
        if not self.session.isOpen():
            raise SerialConnectionError("Session open failed!")
        self.logger.info("Serial session opened.")
        self.session_alive = True

    def _start_reader(self):
        """Start reader thread"""
        self.logger.info("Start reader thread.")
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self.logger.info("Stop reader thread.")
        self._reader_alive = False
        self.receiver_thread.join()

    def _start_session(self):
        try:
            self.logger.debug("Start session.")
            session = serial.Serial(port=self.port,
                                    baudrate=self.baudrate,
                                    timeout=self.read_timeout)
        except SerialConnectionError, e:
            self.logger.error("Error in start session: %s", e)
            session = None
        return session

    def set_rx_encoding(self, encoding='UTF-8', errors='replace'):
        """set encoding for received data"""
        self.input_encoding = encoding
        self.rx_decoder = codecs.getincrementaldecoder(encoding)(errors)
        self.logger.info("Rx encoder setup done.")

    def start(self):
        """start serial session and reader thread"""
        self.log_buffer = LogBuffer()
        self.set_rx_encoding()
        self._start_reader()
        return

    def close(self):
        """close session and reader thread"""
        self._stop_reader()
        self.session.close()
        self.logger.info("Serial session closed as request.")
        self.session_alive = False
        return

    def check_session_alive(self):
        """check serial session alive or not"""
        return self.session.isOpen()

    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.session_alive and self._reader_alive:
                # read all that is there or wait for one byte
                self.logger.debug("Trying to read %d chars.",
                                  self.session.in_waiting)
                data = self.session.read(self.session.in_waiting or 1)
                if data:
                    text = format_asc_log(self.rx_decoder.decode(data))
                    self.logger.debug("Formatted data len %d.", len(text))
                    self.log_buffer.write(text)
        except serial.SerialException:
            self.session_alive = False
            raise SerialConnectionError("Reader got exception.")

    def write(self, content):
        """ write content to serial console"""
        if not self.check_session_alive():
            self.logger.error("Session dead!")
            raise SerialConnectionError("Session closed!")
        self.session.write(content + "\n")
        self.logger.debug("Write to serial session: %s", content)

    def flush_output_to_file(self, file_path):
        """ write serial logs to file"""
        self.log_buffer.flush_to_file(file_path)
        self.logger.debug("Serial logs wrote to file %s.", file_path)

    def empty_output(self):
        """Simply flush to null"""
        self.log_buffer.flush_raw()
        self.logger.debug("Serial logs empty done.")

    def read(self):
        """Got buffer in logs and return"""
        return self.log_buffer.flush_raw()
