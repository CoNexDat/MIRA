#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from pymongo import MongoClient
import pyasn
from bson.objectid import ObjectId


# function to create edges of adjacent ASNS with Traceroute data
def main(version, date):
    # define the db and pyasn file
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['traceroutes']
    edge = db['edges']
    asndb = pyasn.pyasn('ipasns/' + date + '-ipasn-v' + str(version) + '.dat')

    # create an empty DataFrame for the paths
    paths = pd.DataFrame()

    # run for every traceroute with of the campaign with the passed version
    for x in coll.find({'af': version, 'schedule_date': date},
                       {'from': 1, 'dst_addr': 1}):
        # get hop-data from collection
        query = coll.aggregate([{'$match': {'_id': ObjectId(x['_id'])}},
                                {'$unwind': '$result'},
                                {'$project': {'hop': '$result.hop',
                                              'result': '$result.result'}},
                                {'$unwind': '$result'},
                                {'$project': {'hop': '$hop',
                                              'ip': '$result.from'}}])
        # make sure every column exists in case the traceroute contains no data
        df = pd.DataFrame(columns=['_id', 'hop', 'ip'])
        # write data into the DataFrame
        list_results = [r for r in query]
        df = df.append(pd.DataFrame(list_results), sort=False)
        # drop hops without answer
        df = df.dropna(subset=['ip'])
        # reduce entry per traceroute - hop pair to one
        df = df.drop_duplicates(subset=['hop'])

        path = []
        # iterate over every hop in the measurement
        if len(df) > 0:
            _, last = next(df.iterrows())
        for i, row in df.iterrows():
            # get the AS number to the IP address of the hop
            row.ip = asndb.lookup(row.ip)[0]
            # check if the adjacent hops are different
            if(type(row.ip) == int and type(last.ip) == int and
               row.ip != last.ip):
                # add the AS to the path
                path.append(str(row.ip))
                # check if ASes are directly connected
                if last.hop == row.hop - 1:
                    # insert AS-Pair if it doesn't exist
                    # or add date to arrayif not in it yet
                    if(edge.count_documents(
                        {'asn1': {'$in': [last.ip, row.ip]},
                         'asn2': {'$in': [last.ip, row.ip]}}) == 0):
                        edge.insert_one({'asn1': last.ip, 'asn2': row.ip,
                                         'version': version,
                                         'schedule_date': [date]})
                    else:
                        edge.update_one({'asn1': {'$in': [last.ip, row.ip]},
                                         'asn2': {'$in': [last.ip, row.ip]},
                                         'schedule_date': {'$nin': [date]}},
                                        {'$push': {'schedule_date': date}})
                else:
                    path[-1] += '*'
            last = row
        if len(path) > 1:
            paths = paths.append(pd.DataFrame({'source': asndb.lookup(
                x['from'])[0], 'target': asndb.lookup(x['dst_addr'])[0],
                                               'path': [path]}))
    paths.to_csv('paths/' + date + '_paths_v' + str(version)
                 + '.csv', index=False)
