#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time


from ...util import Counter, Timer, ProgressHandler

from .NSLookup import NSLookup


class MultiNSLookup(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x100)
    mutex = threading.Lock()

    def __init__(self, ns_servers, ns_filters, host_names, logger):
        self.ns_servers = ns_servers
        self.ns_filters = ns_filters
        self.host_names = host_names
        self.logger = logger
        self._responses = {}

    def nslookup(self):
        mod_ns = {}
        entry_count = 0
        for mod, hosts in self.host_names.iteritems():
            mod_ns[mod] = self.filter_ns(mod)
            entry_count += (len(hosts) * len(mod_ns[mod]))
        counter = Counter()
        counter.set_total(entry_count)
        timer = Timer(time.time())
        progress_handler = ProgressHandler(counter, timer, self.logger)

        utc_time = timer.format_utc(timer.start_time)
        progress_handler.update_message(
            "Looking for NS records started at " + utc_time)
        progress_handler.update_dash()

        threads = []
        for mod, hosts in self.host_names.iteritems():
            for domain in hosts:
                self.sem.acquire()
                lookup_host = NSLookup(
                    mod_ns[mod], domain, self._responses, counter, self.sem,
                    self.mutex, progress_handler)
                lookup_host.start()
                threads.append(lookup_host)
                time.sleep(0.05)
        for lookup_host in threads:
            lookup_host.join()

        progress_handler.update_dash()
        total_time = timer.format(timer.timer())
        progress_handler.update_message(
            "A total of %d domains were searched in %s" %
            (counter.total, total_time))
        return self._responses

    def filter_ns(self, mod_name):
        ns_filter = self.ns_filters[mod_name]
        ns_results = {}
        if ns_filter == ["ALL"]:
            return self.ns_servers
        elif ns_filter[0] == "!":
            for tag, ip in self.ns_servers.iteritems():
                if tag not in ns_filter:
                    ns_results[tag] = ip
        else:
            for tag, ip in self.ns_servers.iteritems():
                if tag in ns_filter:
                    ns_results[tag] = ip
        return ns_results