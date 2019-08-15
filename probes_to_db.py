#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import pandas as pd
import requests
import filter_probe_data


# function to request and filter all probes in Latin America from RIPE-Atlas
def main(date):
    # configure the and db and collection
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['probes']
    as_coll = db['asns']

    # create empty DataFrame for probes
    all_data = pd.DataFrame(columns=['id', 'country', 'ipv4', 'prefix_v4',
                                     'asn_v4', 'ipv6', 'prefix_v6', 'asn_v6'])

    # get probes from atlas.ripe.net and save it as json-data URL-parameters:
    # https://atlas.ripe.net/docs/api/v2/manual/overview/generic_query_parameters.html
    URL = ("https://atlas.ripe.net/api/v2/probes/?latitude__gte=-54.8"
           + "&latitude__lte=32.6&longitude__gte=-117.1&longitude__lte=-34.8"
           + "&page_size=500")
    data = requests.get(url=URL,
                        proxies=dict(https='socks5://localhost:8080')).json()

    # filter data and add it to the DataFrame
    all_data = all_data.append(filter_probe_data.main(data),
                               ignore_index=True, sort=True)

    # check for more json-data and add it to the DataFrame
    while data['next']:
        data = requests.get(url=data['next'],
                            proxies=dict(
                                https='socks5://localhost:8080')).json()
        all_data = all_data.append(filter_probe_data.main(data),
                                   ignore_index=True, sort=True)

    # remove probes without address & and probes not from Latin America
    all_data = all_data.dropna(subset=['ipv4', 'ipv6']).reset_index(drop=True)
    for x in range(0, len(all_data)):
        if (as_coll.count_documents({'id': str(all_data.at[x, 'asn_v4']),
                                     'schedule_date': date}) == 0
            or as_coll.count_documents({
                'id': str(all_data.at[x, 'asn_v6']),
                'schedule_date': date}) == 0):
            all_data = all_data.drop([x])

    # get one Probe per AS
    all_data = all_data.groupby(['asn_v4', 'asn_v6']).first()

    # update or insert the reduced and filtered DataFrame into the collection
    records_ = all_data.to_dict(orient='records')
    for x in records_:
        if coll.count_documents({'id': x['id']}) == 0:
            x['schedule_date'] = [date]
            coll.insert_one(x)
        else:
            coll.update_one({'id': x['id']},
                            {'$push': {'schedule_date': date}})
