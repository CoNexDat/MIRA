#!/usr/bin/env python
# coding: utf-8


import sys
import json
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import time
import asns_to_db
import probes_to_db
import dl_routeviews
import limit_sources_targets
import create_measurements
import create_fix_measurements
import make_asn_edges
import create_graphs
import create_heatmap


# define the date and db
date = datetime.today().strftime('%Y%m%d')
client = MongoClient()
db = client['conexdat-db']
coll = db['dates']

# transform the passed arguments into a json-dict
args = json.loads(sys.argv[1])

# check if previous measurement was run and get data if not
if coll.count_documents({'date': date}) == 0:
    asns_to_db.main(date)
    probes_to_db.main(date)
    dl_routeviews.main(date)
    coll.insert_one({'date': date})

# create and run the measurements (and save to csv for now)
probes, asns = limit_sources_targets.main(date, int(args['numProbes']),
                                          int(args['numAsns']))

create_measurements.main(
    date, 4, probes, asns, int(args['repetition']), int(args['concurrent']),
    args['description'], args['protocol'], int(args['packets']),
    int(args['first_hop']), int(args['max_hops']), int(args['paris']),
    args['bill_to'], args['api_key'])

create_measurements.main(
    date, 6, probes, asns, int(args['repetition']), int(args['concurrent']),
    args['description'], args['protocol'], int(args['packets']),
    int(args['first_hop']), int(args['max_hops']), int(args['paris']),
    args['bill_to'], args['api_key'])


# sleep to let the writing process to the db finish
time.sleep(600)

# process data and visualize the results for both ip-protocols
make_asn_edges.main(4, date)
make_asn_edges.main(6, date)
create_graphs.main(4, date)
create_graphs.main(6, date)
create_heatmap.main(date)
