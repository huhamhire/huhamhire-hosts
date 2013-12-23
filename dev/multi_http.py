#!/usr/bin/env python
# -*- coding: utf-8 -*

import httplib
import socket
import threading
import time
import sys

from progress import Progress
from source_data import SourceData


class HTTPTest(threading.Thread):
    STATUS_DESC = {
        200: "OK",
        301: "Moved",
        302: "Redirect",
        400: "Bad Request",
        403: "Forbidden",
        404: "Not Found",
        408: "Timed Out",
        500: "Server Error",
        502: "Bad Gateway",
        503: "Unavailable",
        600: "Unknown",
        601: "Conn Reset"
    }
    url = ""
    conn = None
    http_stat = {}
    _response_log = {}

    def __init__(self, ip, domain, comb_id, results, semaphore,
                 req_count=4, timeout=5):
        threading.Thread.__init__(self)
        self._ip = ip
        self._domain = domain
        self._comb_id = comb_id
        self.results = results
        self.sem = semaphore
        self.req_count = req_count
        self.timeout = timeout

    def _set_http_req(self):
        self.url = "http://%s/" % self._domain
        self.conn = httplib.HTTPConnection(host=self._ip,
                                           timeout=self.timeout)

    def _set_https_req(self):
        self.url = "https://%s/" % self._domain
        self.conn = httplib.HTTPSConnection(host=self._ip,
                                            timeout=self.timeout)

    def _check(self):
        start_time = time.time()
        try:
            self.conn.request(method="GET", url=self.url)
            response = self.conn.getresponse()
        except socket.timeout:
            return 408, None
        except socket.error, e:
            if len(e.args) == 1:
                _err_no, _err_msg = 'UNKNOWN', e.args[0]
                if "timed out" in _err_msg:
                    return 408, None
                else:
                    sys.stderr.write("\r  %s - %s: %s\n" %
                                     (self.url, self._ip, _err_msg))
            else:
                _err_no, _err_msg = e.args

            if _err_no == 10054:
                return 601, None
            else:
                return 600, None
        except httplib.BadStatusLine:
            return 600, None
        finally:
            self.conn.close()
        delay = time.time() - start_time
        return response.status, delay

    def session(self):
        response = {}
        try:
            for method in ["http", "https"]:
                status_log = []
                delay_log = []
                for i in range(self.req_count):
                    exec ("self._set_%s_req()" % method)
                    status, delay = self._check()
                    if status not in status_log:
                        status_log.append(status)
                    delay_log.append(delay)
                    time.sleep(0.1)
                response[method] = {"status": status_log,
                                    "delay": delay_log}
                self.show_state(status_log)
            self._response_log = response
        finally:
            self.sem.release()

    def _stat_delay(self, delay_log):
        log = [delay * 1000 for delay in delay_log if delay is not None]
        if log:
            min_delay = round(min(log), 3)
            max_delay = round(max(log), 3)
            avg_delay = round(sum(log) / len(log), 3)
            loss = round(1.0 * len(log) / self.req_count, 3)
            return {"min": min_delay, "max": max_delay,
                    "avg": avg_delay, "ratio": loss}
        else:
            return {"min": None, "max": None,
                    "avg": None, "ratio": 0}

    def _stat_status(self, status_log):
        return "|".join([str(status) for status in sorted(status_log)])

    def stat(self):
        response_log = self._response_log
        stat = {
            "ip": self._ip,
            "domain": self._domain,
            "req_count": self.req_count
        }
        for method, log in response_log.iteritems():
            stat[method] = {"delay": self._stat_delay(log["delay"]),
                            "status": self._stat_status(log["status"])}
        self.http_stat = stat

    def set_results(self):
        self.results[self._comb_id] = self.http_stat

    def show_state(self, status_log):
        msg = "HTTP: %s - %s" % (self.url, self._ip)
        if status_log:
            status_flag = min(status_log)
            if status_flag == 200:
                Progress.show_status(msg, self.STATUS_DESC[status_flag])
            elif status_flag in self.STATUS_DESC.keys():
                Progress.show_status(msg, self.STATUS_DESC[status_flag], 1)
            else:
                Progress.show_status(msg, str(status_flag), 1)
        else:
            Progress.show_status(msg, "NO STATUS", 1)
        Progress.progress_bar()

    def run(self):
        self.session()
        self.stat()
        self.set_results()


class MultiHTTPTest(object):
    # Limit the number of concurrent sessions
    sem = threading.Semaphore(0x100)

    def __init__(self, combinations):
        self.combs = combinations
        self._responses = {}

    def http_test(self):
        Progress.set_total(len(self.combs))
        Progress.set_counter(self._responses)
        threads = []
        for comb in self.combs:
            self.sem.acquire()
            http_test_item = HTTPTest(comb["ip"], comb["domain"], comb["id"],
                                      self._responses, self.sem)
            http_test_item.start()
            threads.append(http_test_item)

        for http_test_item in threads:
            http_test_item.join()

        Progress.progress_bar()
        return self._responses

if __name__ == '__main__':
    SourceData.connect_db()
    combs = SourceData.get_http_test_comb()

    http_tests = MultiHTTPTest(combs)
    results = http_tests.http_test()

    SourceData.set_multi_http_test_dict(results)