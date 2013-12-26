#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.etree.ElementTree import ElementTree

from source_data import SourceData


class SetDomain(object):
    def __init__(self, cfg_file):
        self._cfg_file = cfg_file
        self._name_pool = []
        self._modules = {}
        SourceData.connect_db()

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
        xmlfile = tree.parse(self._cfg_file)
        for module in xmlfile.iter(tag="module"):
            module_name = module.get("name")
            mod_names = []
            mods = module.iter(tag="mod")
            for mod in mods:
                mod_names.append(mod.text)
            self._modules[module_name] = mod_names

    def get_domains_in_mods(self):
        for module, mod_names in self._modules.iteritems():
            for mod in mod_names:
                mod_file = module + "_mods/" + mod + ".hosts"
                domains = self.__get_domains_in_mod(mod_file)
                SourceData.set_multi_domain_list(domains, module + "-" + mod)

    def set_domains(self):
        SourceData.set_multi_domain_list(self._name_pool, "google")


if __name__ == '__main__':
    SourceData.connect_db()
    SourceData.drop_tables()
    SourceData.create_tables()
    SourceData.disconnect_db()

    test = SetDomain("mods.xml")
    test.get_config()
    test.get_domains_in_mods()
    domains = SourceData.get_domain_list()
    for domain in domains:
        print(domain)