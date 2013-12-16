#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import re
import socket
import struct
import threading
import sys

from data import SourceData


class NSTools(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(8)

    @staticmethod
    def encode(host_name):
        index = os.urandom(2)
        host_str = ''.join(chr(len(x)) + x for x in host_name.split('.'))
        data = "%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s" \
               "\x00\x00\x01\x00\x01" % (index, host_str)
        data = struct.pack("!H", len(data)) + data
        return data

    @staticmethod
    def decode(in_sock):
        in_file = in_sock.makefile("rb")
        size = struct.unpack("!H", in_file.read(2))[0]
        data = in_file.read(size)
        ip_list = re.findall("\xC0.\x00\x01\x00\x01.{6}(.{4})", data)
        return [".".join(str(ord(x)) for x in s) for s in ip_list]


class NSLookup(threading.Thread):
    ERROR_DESCR = {
        10054: 'ERROR: Connection reset by peer',
    }
    STATUS_DESCR = {
        0: "OK",
        1: "No Results",
        2: "Timeout",
        3: "Connection Error",
        4: "Decode Error"
    }

    def __init__(self, server_ip, host_name, results,
                 timeout=2, sock_type="TCP", port=53):
        threading.Thread.__init__(self)
        self.server_ip = server_ip
        self.port = port
        self.host_name = host_name
        self.results = results
        self.timeout = timeout
        # Set IP family
        if ":" in server_ip:
            self.ip_family = socket.AF_INET6
        else:
            self.ip_family = socket.AF_INET
            # Set socket type
        if "TCP" == sock_type.upper():
            self.sock_type = socket.SOCK_STREAM
        else:
            self.sock_type = socket.SOCK_DGRAM
        self._response = {"hosts": [], "stat": 1}

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

    def lookup(self):
        sock = self.__sock
        NSTools.sem.acquire()
        try:
            sock.connect((self.server_ip, self.port))
            sock.sendall(NSTools.encode(self.host_name))
            hosts = NSTools.decode(sock)
            self._response["hosts"] = hosts
            if hosts:
                # Set status OK
                self._response["stat"] = 0
            else:
                # Set status No Results
                self._response["stat"] = 1
        except socket.timeout, e:
            sys.stdout.write("\r  host: %s, %s\n" % (self.host_name, e))
            # Set status Timeout
            self._response["stat"] = 2
        except socket.error, (error_no, msg):
            if error_no in self.ERROR_DESCR:
                sys.stdout.write(
                    "\r  host: %s, %s %s\n" %
                    (self.host_name, msg, self.ERROR_DESCR[error_no]))
            # Set status Connection Error
            self._response["stat"] = 3
        except struct.error, e:
            sys.stdout.write("\r  host: %s, %s\n" % (self.host_name, e))
            self._response["stat"] = 4
        finally:
            sock.close()
            NSTools.sem.release()

    def set_result(self):
        self.results[self.host_name] = self._response

    def show_progress(self):
        stat = self.STATUS_DESCR[self._response["stat"]]
        Progress.status(self.host_name, stat)
        Progress.progress_bar(len(self.results))

    def run(self):
        self.lookup()
        self.set_result()
        self.show_progress()


class MultiNSLookup(object):
    def __init__(self, dns_ip, host_names):
        self.server_ip = dns_ip
        self.host_names = host_names
        self._responses = {}

    def nslookup(self):
        threads = []
        name_pool = []
        for host_name in self.host_names:
            if host_name not in name_pool:
                name_pool.append(host_name)
            lookup_host = NSLookup(
                self.server_ip, host_name, self._responses)
            threads.append(lookup_host)

        Progress.set_total(len(name_pool))
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        return self._responses


class Progress(object):
    __line_width = 78
    _total = 0

    @classmethod
    def set_total(cls, total):
        cls._total = total

    @classmethod
    def status(cls, message, status):
        sys.stdout.write("\r%s" % message.ljust(cls.__line_width - 20)
                         + ("[%s]" % status).rjust(20) + "\n")

    @classmethod
    def progress_bar(cls, done_count):
        prog_len = cls.__line_width - 20
        prog = 1.0 * prog_len * done_count / cls._total
        bar = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
        bar = bar.ljust(prog_len)
        count = str(done_count).rjust(7)
        total = str(cls._total).rjust(7)
        progress_bar = "[%s] %s | %s" % (bar, count, total)
        sys.stdout.write("\r" + progress_bar)


if __name__ == '__main__':
    dns_ip = "202.45.84.59"
    in_file = "test.hosts"
    with open(in_file, 'r') as hosts_in:
        host_names = [host_name.rstrip('\n') for host_name in hosts_in]
    lookups = MultiNSLookup(dns_ip, host_names)
    responses = lookups.nslookup()
    # pings = MultiPing(hosts)
    # pings.ping()

    SourceData.connect_db()
    SourceData.drop_tables()
    SourceData.create_tables()
    SourceData.insert_multi_domain_dict(responses)
