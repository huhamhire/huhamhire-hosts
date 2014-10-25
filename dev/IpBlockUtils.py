#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  IpBlockUtils.py:
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================
from itertools import chain

from dev.source_data import SourceData


class IpBlockUtils(object):

    @staticmethod
    def create_v4_ip_block(block_str):
        block = []
        start_ip = block_str.split("/")[0]
        mask = block_str.split("/")[1]
        block_count = 1 << (32 - int(mask))
        generator = 0
        for section in start_ip.split("."):
            generator <<= 8
            generator += int(section)
        ip_count = 1
        while ip_count < block_count - 1:
            raw_ip = generator + ip_count
            address = []
            for i in range(4):
                section = raw_ip & 255
                address.append(str(section))
                raw_ip >>= 8
            address.reverse()
            ip_count += 1
            block.append(".".join(address))
        return block

    @staticmethod
    def create_v6_ip_block(block_str):
        # TODO: IPv6 address blocks
        return

    @staticmethod
    def create_v4_block_by_file(file_path):
        infile = open(file_path, "r")
        blocks = []
        ip_blocks = infile.read().split()
        infile.close()
        for ip_block in ip_blocks:
            if ip_block.startswith("ip4:"):
                ip_block = ip_block.replace("ip4:", "")
                blocks.append(IpBlockUtils.create_v4_ip_block(ip_block))
        return chain(*blocks)

    @staticmethod
    def create_v6_block_by_file(file_path):
        infile = open(file_path, "r")
        blocks = []
        ip_blocks = infile.read().split()
        infile.close()
        for ip_block in ip_blocks:
            if ip_block.startswith("ip6:"):
                ip_block = ip_block.replace("ip6:", "")
                blocks.append(IpBlockUtils.create_v6_ip_block(ip_block))
        return chain(*blocks)

if __name__ == "__main__":
    block_file = "D:/Work/hosts/google_IPs.txt"
    addresses = IpBlockUtils.create_v4_block_by_file(block_file)
    results = {"ma": {"hosts": addresses, "stat": 0}}

    database = "./test.s3db"

    SourceData.connect_db(database)
    SourceData.drop_tables()
    SourceData.create_tables()
    SourceData.set_single_domain("www.google.com", "google")
    SourceData.set_single_ns_response("www.google.com", results)
    SourceData.disconnect_db()