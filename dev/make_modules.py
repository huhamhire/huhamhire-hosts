#!/usr/bin/env python
# -*- coding: utf-8 -*-

from source_data import SourceData


class MakeDomainHost(object):
    def __init__(self, domain_id):
        self._domain_id = domain_id
        self._ping = []
        self._http = []
        self._scores = {}
        self.hosts = []

        if not SourceData.is_connected:
            SourceData.connect_db()

    def set_ping_results(self):
        self._ping = SourceData.get_ping_results_by_domain_id(self._domain_id)

    def set_http_results(self):
        self._http = SourceData.get_http_results_by_domain_id(self._domain_id)

    def set_score(self):
        results = {}
        for ping_result in self._ping:
            if ping_result["avg"]:
                ping_score = ping_result["avg"] / (ping_result["ratio"] ** 2)
                results[ping_result["ip"]] = {"ping": ping_score}
            else:
                results[ping_result["ip"]] = {"ping": 10000}
        for http_result in self._http:
            if http_result["avg"]:
                http_score = http_result["avg"] / (http_result["ratio"] ** 2)
                stats = http_result["status"].split("|")
                http_score *= min([int(stat) for stat in stats]) / 200
                flag = "https" if http_result["ssl"] else "http"
                results[http_result["ip"]][flag] = http_score
            else:
                flag = "https" if http_result["ssl"] else "http"
                results[http_result["ip"]][flag] = 100000

        scores = {}
        for ip, result in results.iteritems():
            score = result["ping"] * 10 + result["http"] + result["https"]
            scores[ip] = int(score * 0.1)
        self._scores = scores

    def make_domain_hosts(self):
        hosts_list = []
        sorted_scores = sorted(
            self._scores.iteritems(),
            key=lambda scores: scores[1])
        results_len = len(sorted_scores)
        m = 3 if results_len < 10 else 5
        for score in sorted_scores:
            hosts_list.append(score[0])
            if len(hosts_list) > results_len * 0.2 and len(hosts_list) > m:
                break
        self.hosts = hosts_list

    def get_domain_hosts(self):
        return self.hosts.reverse()

    def make(self):
        self.set_ping_results()
        self.set_http_results()
        self.set_score()
        self.make_domain_hosts()
        return self.get_domain_hosts()


if __name__ == "__main__":
    mk = MakeDomainHost(169048887)
    mk.make()