#!/usr/bin/env python
# -*- coding: utf-8 -*

from dev.source_data import SourceData

from dev.network.HttpTest import MultiHttpTest


if __name__ == '__main__':
    SourceData.connect_db()
    combs = SourceData.get_http_test_comb()
    ext_combs = SourceData.get_http_test_extend_comb()

    http_tests = MultiHttpTest(combs, ext_combs)
    results = http_tests.http_test()

    SourceData.set_multi_http_test_dict(results)