#!/usr/bin/env python
# -*- coding: utf-8 -*
import threading
import time

from progresshandler import ProgressHandler

from dev.set_domain import SetDomain
from dev.source_data import SourceData

from dev.util.Counter import Counter
from dev.util.Timer import Timer

from NSLookup import NSLookup


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

        ProgressHandler.set_counter(counter)
        ProgressHandler.set_timer(timer)

        utc_time = timer.format_utc(timer.start_time)
        ProgressHandler.show_message(
            "Looking for NS records started at " + utc_time)
        ProgressHandler.dash()

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

        ProgressHandler.dash()
        total_time = timer.format(timer.timer())
        ProgressHandler.show_message(
            "A total of %d domains were searched in %s" %
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
