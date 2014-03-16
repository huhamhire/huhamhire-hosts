#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import re
import socket
import struct
import threading
import time
import sys

from set_domain import SetDomain

from progress import Progress
from source_data import SourceData

from util.Counter import Counter
from util.Timer import Timer


class NSTools(object):

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
                 ipv6=False, timeout=2, sock_type="TCP", port=53):
        threading.Thread.__init__(self)
        self.servers = servers
        self.port = port
        self.host_name = host_name
        self.results = results
        self.counter = counter
        self.sem = semaphore
        self.mutex = mutex
        self.timeout = timeout

        # Set IP family
        if ipv6:
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
            sock.sendall(NSTools.encode(self.host_name))
            hosts = NSTools.decode(sock)
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
            Progress.show_status(msg, stat)
        else:
            Progress.show_status(msg, stat, 1)
        Progress.progress_bar()
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


class MultiNSLookup(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x20)
    mutex = threading.Lock()

    def __init__(self, ns_servers, host_names):
        self.ns_servers = ns_servers
        self.host_names = host_names
        self._responses = {}

    def nslookup(self):
        counter = Counter()
        counter.set_total(len(self.host_names) * len(self.ns_servers))
        timer = Timer(time.time())

        Progress.set_counter(counter)
        Progress.set_timer(timer)

        utc_time = timer.format_utc(timer.start_time)
        Progress.show_message("Looking for NS records started at " + utc_time)
        Progress.dash()

        threads = []
        for domain in self.host_names:
            self.sem.acquire()
            lookup_host = NSLookup(
                self.ns_servers, domain, self._responses, counter, self.sem,
                self.mutex)
            lookup_host.start()
            threads.append(lookup_host)

        for lookup_host in threads:
            lookup_host.join()

        Progress.dash()
        total_time = timer.format(timer.timer())
        Progress.show_message("A total of %d domains were searched in %s" %
                              (counter.total, total_time))

        return self._responses


if __name__ == '__main__':
    ns_servers = {
        "us": "64.118.80.141",
        "uk": "62.140.195.84",
        "de": "62.128.1.42",
        "fr": "82.216.111.121",

        "cn": "211.157.15.189",
        "hk": "203.80.96.10",
        "tw": "168.95.192.1",
        "jp": "158.205.225.226",
        "sg": "165.21.83.88",
        "kr": "115.68.45.3",
        "in": "58.68.121.230",
    }
    cfg_file = "mods.xml"
    set_domain = SetDomain(cfg_file)
    set_domain.get_config()
    set_domain.get_domains_in_mods()
    domains = SourceData.get_domain_list()

    lookups = MultiNSLookup(ns_servers, domains)
    responses = lookups.nslookup()

    SourceData.set_multi_ns_response(responses)
