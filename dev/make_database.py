#!/usr/bin/env python
# -*- coding: utf-8 -*

from source_data import SourceData

def make_database():
    SourceData.connect_db()
    SourceData.drop_tables()
    SourceData.clear()
    SourceData.create_tables()

if __name__ == '__main__':
    make_database()