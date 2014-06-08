#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from xml.etree.ElementTree import ElementTree

from source_data import SourceData


class SetDomain(object):
    def __init__(self, cfg_path, cfg_file, database="test.s3db"):
        self._cfg_path = cfg_path
        self._cfg_file = cfg_file
        self._name_pool = []
        self._modules = {}
        self._ns_filter = {}
        self._predefined_nodes = {}

        if not SourceData.is_connected:
            SourceData.connect_db(database)

    def __get_domains_in_mod(self, mod_file):
        domains = []
        with open(mod_file, 'r') as hosts_in:
            lines = [host_name.rstrip('\n') for host_name in hosts_in]
        for line in lines:
            if not line.startswith("#") \
                    and len(line) > 3 \
                    and line not in domains:
                domains.append(line)
        return domains

    def get_config(self):
        tree = ElementTree()
        cfg_file = path.join(self._cfg_path, self._cfg_file)
        xmlfile = tree.parse(cfg_file)
        for module in xmlfile.iter(tag="module"):
            module_name = module.get("name")
            mod_names = []
            mods = module.iter(tag="mod")
            for mod in mods:
                mod_name = mod.get("func")
                mod_names.append(mod_name)
                full_mod_name = module_name + "-" + mod_name
                self._ns_filter[full_mod_name] = mod.get("ns").split(",")
                nodes = mod.iter(tag="node")
                node_records = []
                for node in nodes:
                    node_records.append(node.text)
                self._predefined_nodes[full_mod_name] = node_records
            self._modules[module_name] = mod_names

    def get_domains_in_mods(self):
        for module, mod_names in self._modules.iteritems():
            for mod in mod_names:
                mod_file = module + "/" + mod + ".hosts"
                mod_file = path.join(self._cfg_path, mod_file)
                domains = self.__get_domains_in_mod(mod_file)
                full_mod_name = module + "-" + mod
                SourceData.set_multi_domain_list(domains, full_mod_name)
                predefined_nodes = self._predefined_nodes.get(full_mod_name)
                if predefined_nodes:
                    for node in predefined_nodes:
                        SourceData.set_multi_predefined_domain_ip(domains, node)


    def get_ns_filters(self):
        return self._ns_filter


if __name__ == '__main__':
    if not SourceData.is_connected:
        SourceData.connect_db()

    SourceData.drop_tables()
    SourceData.create_tables()
    SourceData.disconnect_db()

    test = SetDomain("./modules/", "modules.xml")
    test.get_config()
    test.get_domains_in_mods()
    domains = SourceData.get_domain_list()
    for domain in domains:
        print(domain)