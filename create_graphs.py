#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import pandas as pd
import create_asn_map
import create_degree_graphs


# function to create a network-map of the AS-data using LaNet-vi
def main(version, date):
    # define the db and pyasn file
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['edges']

    # write edge-data into DataFrame
    query = coll.aggregate([{'$match': {'version': version,
                                        'schedule_date': date}},
                            {'$project': {'asn1': '$asn1',
                                          'asn2': '$asn2', '_id': 0}}])
    list_results = [r for r in query]
    df = pd.DataFrame(list_results)
    df = df.sort_values(['asn1']).reset_index(drop=True)

    # pass DataFrame to the functions to create and save the graphics
    create_asn_map.main(version, date, df)
    create_degree_graphs.main(version, date, df)
