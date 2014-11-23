#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ssl
import pprint
from socket import socket

soc = ssl.SSLSocket(socket(),
                    ca_certs='E:/Projects/hostschecker/ca-bundle.crt',
                    cert_reqs=ssl.CERT_REQUIRED)
soc.connect(("74.125.200.197", 443))
cert = soc.getpeercert()
soc.close()

pprint.pprint(cert)
