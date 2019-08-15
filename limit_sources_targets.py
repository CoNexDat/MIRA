#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from pymongo import MongoClient
import filter_asns


# method to limit the sources and targets of a measurement according to
# numProbes for the number of probes and numAsns for the number of ASes
def main(date, numProbes, numAsns):
    # define the date and db
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['probes']

    # get list of probes
    probes = pd.DataFrame(list(coll.find({'schedule_date': {'$in': [date]}},
                                         {'_id': 0, 'id': 1})))

    # get list of valid asns
    asns = filter_asns.main(date)

    # limit size of probes and asns according to the passed parameters
    if numProbes > 0:
        try:
            probes = probes.sample(n=numProbes)
            probes = probes.reset_index(drop=True)
        except Exception:
            pass
    if numAsns > 0:
        try:
            asns = asns.sample(n=numAsns)
            asns = asns.reset_index(drop=True)
        except Exception:

            pass

    return probes, asns
