#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time

from ...util import Counter, Timer, ProgressHandler

from .PingTest import PingTest


class MultiPingTest(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x200)
    mutex = threading.Lock()

    def __init__(self, combinations, logger):
        self.combs = combinations
        self._responses = {}
        self.logger = logger

    def ping_test(self):
        counter = Counter()
        counter.set_total(len(self.combs))
        timer = Timer(time.time())
        progress_handler = ProgressHandler(counter, timer, self.logger)

        utc_time = timer.format_utc(timer.start_time)
        progress_handler.update_message("Ping tests started at " + utc_time)
        progress_handler.update_dash()

        threads = []
        for comb in self.combs:
            self.sem.acquire()
            ping_host = PingTest(
                comb["ip"], comb["ip_id"], self._responses, counter, self.sem,
                self.mutex, progress_handler)
            ping_host.start()
            threads.append(ping_host)
            time.sleep(0.05)
        for ping_host in threads:
            ping_host.join()

        progress_handler.update_dash()
        total_time = timer.format(timer.timer())
        progress_handler.update_message(
            "A total of %d Ping tests were operated in %s" %
            (counter.total, total_time))
        return self._responses
