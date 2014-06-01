#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time

from ...util import Counter, Timer, ProgressHandler

from .HTTPTest import HttpTest


class MultiHttpTest(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x200)
    mutex = threading.Lock()

    def __init__(self, combinations, ext_combinations, logger):
        self.combs = combinations
        self.ext_combs = ext_combinations
        self.logger = logger
        self._responses = {}
        self.results = {}

    def http_test(self):
        counter = Counter()
        counter.set_total(len(self.combs) * 2)
        timer = Timer(time.time())
        progress_handler = ProgressHandler(counter, timer, self.logger)

        utc_time = timer.format_utc(timer.start_time)
        progress_handler.update_message("HTTP tests started at " + utc_time)
        progress_handler.update_dash()

        threads = []
        for comb in self.combs:
            self.sem.acquire()
            http_test_item = HttpTest(
                comb["ip"], comb["domain"], comb["id"], self._responses,
                counter, self.sem, self.mutex, progress_handler)
            http_test_item.start()
            threads.append(http_test_item)
            time.sleep(0.05)
        for http_test_item in threads:
            http_test_item.join()

        progress_handler.update_dash()
        total_time = timer.format(timer.timer())
        progress_handler.update_message(
            "A total of %d HTTP tests were operated in %s" %
            (counter.total, total_time))
        return self._responses
