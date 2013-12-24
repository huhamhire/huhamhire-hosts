__author__ = 'Hamhire'

from source_data import SourceData


class SetDomain(object):
    def __init__(self, in_file):
        self._in_file = in_file
        self._name_pool = []
        self.__get_domains()

    def __get_domains(self):
        with open(self._in_file, 'r') as hosts_in:
            host_names = [host_name.rstrip('\n') for host_name in hosts_in]
        for domain in host_names:
            if domain not in self._name_pool:
                self._name_pool.append(domain)

    def set_domains(self):
        SourceData.connect_db()
        SourceData.set_multi_domain_list(self._name_pool, "google")

    def get_domains(self):
        return self._name_pool