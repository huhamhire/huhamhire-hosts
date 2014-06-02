#!/usr/bin/env python
# -*- coding: utf-8 -*

import threading
import time


from ...util import Counter, Timer, ProgressHandler

from .NSLookup import NSLookup


class MultiNSLookup(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x80)
    mutex = threading.Lock()

    def __init__(self, ns_servers, ns_filters, host_names, logger,
                 v6_query = False, v6_socket=False):
        self.ns_servers = ns_servers
        self.ns_filters = ns_filters
        self.host_names = host_names
        self.logger = logger
        self.v6_query = v6_query
        self.v6_socket = v6_socket
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
                    self.mutex, progress_handler, self.v6_query, self.v6_socket)
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
        ns_filters = self.ns_filters[mod_name]
        ns_results = {}
        if ns_filters == ["ALL"]:
            return self.ns_servers
        else:
            for tag, ip in self.ns_servers.iteritems():
                if ns_filters[0] == "!":
                    if tag not in ns_filters:
                        ns_results[tag] = ip
                else:
                    if tag in ns_filters:
                        ns_results[tag] = ip
        return ns_results