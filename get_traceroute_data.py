#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import pyasn
from pymongo import MongoClient


def main(version, date):
    # define the db and pyasn file
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['traceroutes']
    as_coll = db['asns']
    asndb = pyasn.pyasn('ipasns/' + date + '-ipasn-v' + str(version) + '.dat')

    # make DataFrame for every Traceroute
    data = pd.DataFrame()

    # get Traceroute-Data for every measurement with of the passed version
    for x in coll.distinct('msm_id', {'af': version, 'schedule_date': date}):
        # get hop-data from collection and make a DataFrame
        query = coll.aggregate([{'$match': {'msm_id': x}},
                                {'$unwind': '$result'},
                                {'$project': {'_id': '$_id',
                                              'dst': '$dst_addr',
                                              'src': '$from',
                                              'hop': '$result.hop',
                                              'result': '$result.result'}},
                                {'$unwind': '$result'},
                                {'$project': {'_id': '$_id',
                                              'dst': '$dst',
                                              'src': '$src',
                                              'hop': '$hop',
                                              'rtt': '$result.rtt'}}])
        list_results = [r for r in query]
        df = pd.DataFrame(list_results)
        # drop false src-data, hops without or bad answer
        # and hops that timed out (hop = 255)
        df = df.dropna()
        df = df[(df['hop'] < 255) & (df['rtt'] > 0.0) & (df['src'] != '')]
        # group hops to get the median of all RTTs of a single hop
        df = df.groupby(['_id', 'hop', 'dst', 'src']).median()
        df = df.reset_index(level=['hop', 'dst', 'src'])
        # drop hops because they aren't needed
        df = df.drop(columns=['hop'])
        # reduce traceroutes to last succesful result
        df = df.groupby(['_id']).last()

        # replace source and destination with their Country
        for i, row in df.iterrows():
            for x in as_coll.find({'id': str(asndb.lookup(df.at[i, 'dst'])[0]),
                                   'schedule_date': date},
                                  {'country': 1}):
                df.at[i, 'dst'] = x['country']
            for x in as_coll.find({'id': str(asndb.lookup(df.at[i, 'src'])[0]),
                                   'schedule_date': date},
                                  {'country': 1}):
                df.at[i, 'src'] = x['country']

        # append results to DataFrame
        data = data.append(df, ignore_index=True)

    # group data by the med of the RTT by src- and dst-Country
    data = data.groupby(['dst', 'src']).median()

    # transform data into a pivot-table
    data = data.pivot_table(index='src', columns='dst', values='rtt')

    # return the DataFrame
    return data
