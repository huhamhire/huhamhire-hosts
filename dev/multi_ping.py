#!/usr/bin/env python
# -*- coding: utf-8 -*

import array
import random
import socket
import struct
import threading
import time
import select

from progress import Progress
from source_data import SourceData

from util.Counter import Counter
from util.Timer import Timer


class PingHost(threading.Thread):
    ERROR_DESCR = {
        1: 'ERROR: ICMP messages can only be sent from processes running as '
           'root.',
        10013: 'ERROR: ICMP messages can only be sent by users or processes '
               'with administrator rights.',
        10049: 'ERROR: "%s" is not available from the local computer',
    }

    def __init__(self, ip, ip_id, results, counter, semaphore, mutex,
                 ping_count=4, timeout=5, v6_flag=False):
        threading.Thread.__init__(self)
        self.__data = struct.pack('d', time.time())
        self._pid = 0
        self._pack = None

        self._ip = ip
        self._ip_id = ip_id
        self._ping_count = ping_count
        self.results = results
        self.counter = counter
        self.sem = semaphore
        self.mutex = mutex
        self._timeout = timeout
        self._v6_flag = v6_flag

        self.time_log = []
        self.delay_stat = {}

        self._sock = self.__sock

    @property
    def __sock(self):
        try:
            if not self._v6_flag:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                     socket.getprotobyname("icmp"))
            else:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW,
                                     socket.getprotobyname("ipv6-icmp"))
                sock.settimeout(self._timeout)
            return sock
        except socket.error, (error_no, msg):
            if error_no in self.ERROR_DESCR:
                raise socket.error(msg + self.ERROR_DESCR[error_no])
            raise

    @property
    def __pack(self):
        if not self._v6_flag:
            header = struct.pack('bbHHh', 8, 0, 0, self._pid, 0)
        else:
            header = struct.pack('BbHHh', 128, 0, 0, self._pid, 0)

        pack = header + self.__data
        checksum = self.__checksum(pack)

        if not self._v6_flag:
            header = struct.pack('bbHHh', 8, 0, checksum, self._pid, 0)
        else:
            header = struct.pack('BbHHh', 128, 0, checksum, self._pid, 0)
        return header + self.__data

    def __checksum(self, pack):
        if len(pack) & 1:
            pack += '\0'
        words = array.array('h', pack)
        sum = 0
        for word in words:
            sum += (word & 0xffff)
        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)
        return (~sum) & 0xffff

    def send(self):
        pack = self._pack
        while pack:
            sent = self._sock.sendto(pack, (self._ip, 0))
            pack = pack[sent:]
        self.time_sent = time.time()

    def response(self):
        while True:
            timeout = self._timeout
            ready = select.select([self._sock], [], [], timeout)
            if not ready[0]:
                return None
            time_received = time.time()
            rec_packet, address = self._sock.recvfrom(1024)
            header = rec_packet[20:28]
            rtype, code, checksum, rid, seq = struct.unpack('bbHHh', header)
            if rid == self._pid:
                return time_received - self.time_sent
            timeout -= (time_received - self.time_sent)
            if timeout <= 0:
                return None

    def session(self):
        try:
            time_log = []
            for i in range(self._ping_count):
                self._pid = int((id(self._timeout) * random.random()) % 65535)
                self._pack = self.__pack
                self.send()
                delay = self.response()
                time_log.append(delay)
                time.sleep(1)
            self._sock.close()
            self.time_log = time_log
        except socket.error, (error_no, msg):
            self.time_log = [None for i in range(self._ping_count)]
            if error_no in self.ERROR_DESCR:
                msg += self.ERROR_DESCR[error_no]
                if "%s" in msg:
                    print(msg % self._ip)
                else:
                    print(msg)
            else:
                raise
        finally:
            self.sem.release()

    def stat(self):
        log = self.time_log
        log = [delay * 1000 for delay in log if delay is not None]
        if log:
            min_delay = round(min(log), 3)
            max_delay = round(max(log), 3)
            avg_delay = round(sum(log) / len(log), 3)
            loss = round(1.0 * len(log) / self._ping_count, 3)
            self.delay_stat = {"min": min_delay, "max": max_delay,
                               "avg": avg_delay, "ratio": loss}
        else:
            self.delay_stat = {"min": None, "max": None,
                               "avg": None, "ratio": 0}
        self.delay_stat["ping_count"] = self._ping_count
        self.counter.inc()

    def set_results(self):
        self.results[self._ip_id] = self.delay_stat

    def show_state(self):
        msg = "PING: %s" % self._ip
        self.mutex.acquire()
        if self.delay_stat["ratio"] == 1:
            Progress.show_status(msg, "OK")
        else:
            if self.delay_stat["ratio"] > 0:
                status = "Packet Loss"
            else:
                status = "Failed"
            Progress.show_status(msg, status, 1)
        Progress.progress_bar()
        self.mutex.release()

    def run(self):
        self.session()
        self.stat()
        self.set_results()
        self.show_state()


class MultiPing(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x100)
    mutex = threading.Lock()

    def __init__(self, combinations):
        self.combs = combinations
        self._responses = {}

    def ping_test(self):
        counter = Counter()
        counter.set_total(len(self.combs))
        timer = Timer(time.time())

        Progress.set_counter(counter)
        Progress.set_timer(timer)

        utc_time = timer.format_utc(timer.start_time)
        Progress.show_message("Ping tests started at " + utc_time)
        Progress.dash()

        threads = []
        for comb in self.combs:
            self.sem.acquire()
            ping_host = PingHost(comb["ip"], comb["ip_id"], self._responses,
                                 counter, self.sem, self.mutex)
            ping_host.start()
            threads.append(ping_host)

        for ping_host in threads:
            ping_host.join()

        Progress.dash()
        total_time = timer.format(timer.timer())
        Progress.show_message("A total of %d Ping tests were operated in %s" %
                              (counter.total, total_time))

        return self._responses


if __name__ == '__main__':
    SourceData.connect_db()
    combs = SourceData.get_ping_test_comb()

    ping_tests = MultiPing(combs)
    results = ping_tests.ping_test()

    SourceData.set_multi_ping_test_dict(results)