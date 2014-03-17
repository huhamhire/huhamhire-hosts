#!/usr/bin/env python
# -*- coding: utf-8 -*

from dev.source_data import SourceData

from dev.network.PingTest import MultiPingTest


if __name__ == '__main__':
    SourceData.connect_db()
    combs = SourceData.get_ping_test_comb()

    ping_tests = MultiPingTest(combs)
    results = ping_tests.ping_test()

    SourceData.set_multi_ping_test_dict(results)