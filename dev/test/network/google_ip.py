#!/usr/bin/env python
# -*- coding: utf-8 -

import os
import re
from dev.source_data import SourceData

WORK_DIR = "E:/Project/Hosts/Google-IPs/"

source = open(os.path.join(WORK_DIR, "README.md"), "r")
test = source.read()
source.close()

ip_re = r"\d+.\d+.\d+.\d+"
match_re = r"target=\"_blank\">(%s)</a></td>" % ip_re
pattern = re.compile(match_re)

ips = pattern.findall(test)

# target = open(os.path.join(WORK_DIR, "google_ip.txt"), "w")
# target.write("\n".join(ips))
# target.close()

results = {"ma": {"hosts": ips, "stat": 0}}

SourceData.connect_db("../../test.s3db")
SourceData.set_single_ns_response("www.google.com", results)