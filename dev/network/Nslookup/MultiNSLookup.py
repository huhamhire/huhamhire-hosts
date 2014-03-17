#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time


from ...util import Counter, Timer, ProgressHandler

from .NSLookup import NSLookup


class MultiNSLookup(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x20)
    mutex = threading.Lock()

    def __init__(self, ns_servers, host_names, logger):
        self.ns_servers = ns_servers
        self.host_names = host_names
        self.logger = logger
        self._responses = {}

    def nslookup(self):
        counter = Counter()
        counter.set_total(len(self.host_names) * len(self.ns_servers))
        timer = Timer(time.time())
        progress_handler = ProgressHandler(counter, timer, self.logger)

        utc_time = timer.format_utc(timer.start_time)
        progress_handler.update_message(
            "Looking for NS records started at " + utc_time)
        progress_handler.update_dash()

        threads = []
        for domain in self.host_names:
            self.sem.acquire()
            lookup_host = NSLookup(
                self.ns_servers, domain, self._responses, counter, self.sem,
                self.mutex, progress_handler)
            lookup_host.start()
            threads.append(lookup_host)
        for lookup_host in threads:
            lookup_host.join()

        progress_handler.update_dash()
        total_time = timer.format(timer.timer())
        progress_handler.update_message(
            "A total of %d domains were searched in %s" %
            (counter.total, total_time))
        return self._responses
