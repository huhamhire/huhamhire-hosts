#!/usr/bin/env python
# -*- coding: utf-8 -*

from dev.set_domain import SetDomain
from dev.source_data import SourceData

from dev.network.nslookup import MultiNSLookup

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