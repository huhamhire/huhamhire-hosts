#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time

from progresshandler import ProgressHandler

from dev.source_data import SourceData

from dev.util.Counter import Counter
from dev.util.Timer import Timer

from PingTest import PingTest


class MultiPingTest(object):
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

        ProgressHandler.set_counter(counter)
        ProgressHandler.set_timer(timer)

        utc_time = timer.format_utc(timer.start_time)
        ProgressHandler.show_message("Ping tests started at " + utc_time)
        ProgressHandler.dash()

        threads = []
        for comb in self.combs:
            self.sem.acquire()
            ping_host = PingTest(comb["ip"], comb["ip_id"], self._responses,
                                 counter, self.sem, self.mutex)
            ping_host.start()
            threads.append(ping_host)

        for ping_host in threads:
            ping_host.join()

        ProgressHandler.dash()
        total_time = timer.format(timer.timer())
        ProgressHandler.show_message(
            "A total of %d Ping tests were operated in %s" %
            (counter.total, total_time))

        return self._responses


if __name__ == '__main__':
    SourceData.connect_db()
    combs = SourceData.get_ping_test_comb()

    ping_tests = MultiPingTest(combs)
    results = ping_tests.ping_test()

    SourceData.set_multi_ping_test_dict(results)