#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time

from progresshandler import ProgressHandler

from dev.source_data import SourceData
from dev.util.Counter import Counter
from dev.util.Timer import Timer

from HttpTest import HttpTest


class MultiHttpTest(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x100)
    mutex = threading.Lock()

    def __init__(self, combinations, ext_combinations):
        self.combs = combinations
        self.ext_combs = ext_combinations
        self._responses = {}
        self.results = {}

    def http_test(self):
        counter = Counter()
        counter.set_total(len(self.combs) * 2)
        timer = Timer(time.time())

        ProgressHandler.set_counter(counter)
        ProgressHandler.set_timer(timer)

        utc_time = timer.format_utc(timer.start_time)
        ProgressHandler.show_message("HTTP tests started at " + utc_time)
        ProgressHandler.dash()

        threads = []
        for comb in self.combs:
            self.sem.acquire()
            http_test_item = HttpTest(comb["ip"], comb["domain"], comb["id"],
                                      self._responses, counter,
                                      self.sem, self.mutex)
            http_test_item.start()
            threads.append(http_test_item)

        for http_test_item in threads:
            http_test_item.join()

        ProgressHandler.dash()
        total_time = timer.format(timer.timer())
        ProgressHandler.show_message(
            "A total of %d HTTP tests were operated in %s" %
            (counter.total, total_time))
        return self._responses


if __name__ == '__main__':
    SourceData.connect_db()
    combs = SourceData.get_http_test_comb()
    ext_combs = SourceData.get_http_test_extend_comb()

    http_tests = MultiHttpTest(combs, ext_combs)
    results = http_tests.http_test()

    SourceData.set_multi_http_test_dict(results)