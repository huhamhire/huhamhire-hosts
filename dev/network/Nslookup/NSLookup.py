#!/usr/bin/env python
# -*- coding: utf-8 -*
import socket
import struct
import sys
import threading

from NSUtils import NSUtils


class NSLookup(threading.Thread):
    ERROR_DESC = {
        10054: 'ERROR: Connection reset by peer',
    }
    STATUS_DESC = {
        0: "OK",
        1: "No Match",
        2: "Timed Out",
        3: "Conn Err",
        4: "Decode Err"
    }

    def __init__(self, servers, host_name, results, counter, semaphore, mutex,
                 progress_handler, v6_query = False, v6_socket=False,
                 timeout=10, sock_type="TCP", port=53):
        threading.Thread.__init__(self)
        self.servers = servers
        self.port = port
        self.host_name = host_name
        self.results = results
        self.counter = counter
        self.sem = semaphore
        self.mutex = mutex
        self.p_handler = progress_handler
        self.timeout = timeout

        self._response = {}

        # Set IP query
        if v6_query:
            self.encode = NSUtils.encode_v6
            self.decode = NSUtils.decode_v6
        else:
            self.encode = NSUtils.encode_v4
            self.decode = NSUtils.decode_v4
        # Set IP family
        if v6_socket:
            self.ip_family = socket.AF_INET6
        else:
            self.ip_family = socket.AF_INET
        # Set socket type
        if "TCP" == sock_type.upper():
            self.sock_type = socket.SOCK_STREAM
        else:
            self.sock_type = socket.SOCK_DGRAM
        self.results[host_name] = {}

    @property
    def __sock(self):
        try:
            sock = socket.socket(self.ip_family, self.sock_type)
            sock.settimeout(self.timeout)
            return sock
        except socket.error, (error_no, msg):
            sys.stdout.write("\r  host: %s, Error %d: %s\n" %
                             (self.host_name, error_no, msg))
            raise

    def lookup(self, server_ip):
        sock = self.__sock
        try:
            sock.connect((server_ip, self.port))
            sock.sendall(self.encode(self.host_name))
            hosts = self.decode(sock)
            self._response["hosts"] = hosts
            if hosts:
                # Set status OK
                self._response["stat"] = 0
            else:
                # Set status No Results
                self._response["stat"] = 1
        except socket.timeout:
            # Set status Timeout
            self._response["stat"] = 2
        except socket.error:
            # Set status Connection Error
            self._response["stat"] = 3
        except struct.error:
            # Set status Decode Error
            self._response["stat"] = 4
        finally:
            sock.close()

    def show_state(self, server_tag):
        stat = self.STATUS_DESC[self._response["stat"]]
        msg = "NSLK: " + self.host_name + " - " + server_tag
        self.mutex.acquire()
        if stat == "OK":
            self.p_handler.update_status(msg, stat)
        else:
            self.p_handler.update_status(msg, stat, 1)
        self.p_handler.update_progress()
        self.mutex.release()

    def run(self):
        responses = {}
        for tag, ip in self.servers.iteritems():
            self._response = {"hosts": [], "stat": 1}
            self.lookup(ip)
            responses[tag] = self._response
            self.counter.inc()
            self.show_state(tag)
        self.results[self.host_name] = responses
        self.sem.release()