#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.etree.ElementTree import ElementTree

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
            if len(hosts_list) > results_len * 0.2 and len(hosts_list) >= m:
                break
        self.hosts = hosts_list

    def get_domain_hosts(self):
        hosts = self.hosts
        hosts.reverse()
        return hosts

    def make(self):
        self.set_ping_results()
        self.set_http_results()
        self.set_score()
        self.make_domain_hosts()


class MakeDomainModule(object):
    def __init__(self, module_tag):
        self._tag = module_tag
        self._domains = []
        self.module = {}

        if not SourceData.is_connected:
            SourceData.connect_db()

    def set_domains(self):
        self._domains = SourceData.get_domains_by_module_tag(self._tag)

    def make_module(self):
        for domain in self._domains:
            mk_host = MakeDomainHost(domain["id"])
            mk_host.make()
            hosts = mk_host.get_domain_hosts()
            if hosts:
                self.module[domain["domain"]] = hosts

    def get_module(self):
        return self.module

    def make(self):
        self.set_domains()
        self.make_module()


class MakeModuleFile(object):
    def __init__(self, cfg_file):
        self._cfg_file = cfg_file
        self._modules = {}

    def get_config(self):
        # Same as SetDomain
        tree = ElementTree()
        xmlfile = tree.parse(self._cfg_file)
        for module in xmlfile.iter(tag="module"):
            module_name = module.get("name")
            mod_names = []
            mods = module.iter(tag="mod")
            for mod in mods:
                mod_names.append(mod.text)
            self._modules[module_name] = mod_names

    def set_hosts_in_mod(self, module, mod):
        hosts = []
        mod_file = module + "_mods/" + mod + ".hosts"
        mod_tag = module + "-" + mod
        make_mod = MakeDomainModule(mod_tag)
        make_mod.make()
        mod_hosts = make_mod.get_module()
        with open(mod_file, 'r') as hosts_in:
            lines = [host_name.rstrip('\n') for host_name in hosts_in]
        for line in lines:
            if not line.startswith("#") \
                    and len(line) > 3 \
                    and line not in hosts:
                domain = line
                if domain not in mod_hosts.keys():
                    pass
                else:
                    for ip in mod_hosts[domain]:
                        hosts.append(ip.ljust(18) + domain + "\n")
            else:
                hosts.append(line + "\n")
        return hosts

    def make_module_file(self, hosts, module, mod):
        file_name = module + "_out/" + mod + ".hosts"
        out_file = open(file_name, "w")
        out_file.writelines(hosts)
        out_file.close()

    def make_modules_from_mods(self):
        for module, mod_names in self._modules.iteritems():
            for mod in mod_names:
                hosts = self.set_hosts_in_mod(module, mod)
                self.make_module_file(hosts, module, mod)


if __name__ == "__main__":
    mk = MakeModuleFile("mods.xml")
    mk.get_config()
    mk.make_modules_from_mods()