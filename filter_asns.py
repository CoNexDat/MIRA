#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import pandas as pd
import pyasn
import ipaddress


# function to eliminate ASNS without IPv6- or IPv4-Prefix
def main(date):
    # configure the and db and collection
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['asns']

    # open pyasn-v6 db
    asndb = pyasn.pyasn('ipasns/' + date + '-ipasn-v6.dat')

    # create empty DataFrame for ASNS
    asns = pd.DataFrame(columns=['id', 'ipv4', 'ipv6'])

    # get AS with cone-size = 1
    for x in coll.find({'cone.asns': {'$eq': 1},
                        'schedule_date': {'$in': [date]}},
                       {'_id': 0, 'id': 1}):
        # lookup ASv6-prefixes and add the AS to the list if it has any
        a = asndb.get_as_prefixes(x['id'])
        if not isinstance(a, type(None)) and len(a) > 0:
            # use try to avoid prefixes without valid hosts
            try:
                asns = asns.append(
                        pd.DataFrame({'id': [x['id']], 'ipv4': None,
                                      'ipv6': next(ipaddress.ip_network(
                                        a.pop()).hosts())}), ignore_index=True)
            except Exception:
                pass
    # open pyasn-v4 db
    asndb = pyasn.pyasn('ipasns/' + date + '-ipasn-v4.dat')

    # eliminate AS without IPv4-prefix from the list
    for x in range(0, len(asns)):
        a = asndb.get_as_prefixes(asns['id'][x])
        # lookup AS-prefixes and add the AS to the list if it has any
        if not isinstance(a, type(None)) and len(a) > 0:
            # use try to avoid prefixes without valid hosts
            try:
                asns['ipv4'][x] = list(ipaddress.ip_network(a.pop())
                                       .hosts())[0]
            except Exception:
                asns = asns.drop([x])
        else:
            asns = asns.drop([x])

    # reindex DataFrame to secure iterate works as intended
    asns = asns.reset_index(drop=True)

    return asns
