#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import requests


# function to insert every asn in Latin America from CAIDA AS-Rank
# into the DB-collection
def main(date):
    # configure the and db and collection
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['asns']

    # define countries in Latin America according to LANIC
    countries = [
        'AG', 'AR', 'AW', 'BS', 'BB', 'BZ', 'BO', 'BR', 'KY', 'CL', 'CO', 'CR',
        'CU', 'DM', 'DO', 'EC', 'SV', 'GF', 'GD', 'GP', 'GT', 'GY', 'HT', 'HN',
        'JM', 'MQ', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'BL', 'KN', 'LC', 'VC',
        'SR', 'TT', 'TC', 'VI', 'UY', 'VE'
        ]

    # get the total number to asns to calculate the need amount of pages
    # (page-size = 500)
    URL = "http://as-rank.caida.org/api/v1/asns"
    r = requests.get(url=URL).json()
    total = int(r['total']/500)+1

    # get asn-data from http://as-rank.caida.org and save it as json-data
    for x in range(0, total):
        URL = ("http://as-rank.caida.org/api/v1/asns?populate=1&count=500"
               + "&page=" + str(x+1))
        data = requests.get(url=URL).json()
        # iterate over every asn in the response
        for y in range(0, len(data['data'])):
            try:
                # check if the geo-position of the asn is in Latin America
                if(-54.8 < float(data['data'][y]['latitude']) < 32.6
                   and -117.1 < float(data['data'][y]['longitude']) < -34.8
                   and data['data'][y]['country'] in countries):
                    # insert the data into the db
                    if(coll.count_documents({'id': data['data'][y]['id']})
                       == 0):
                        data['data'][y]['schedule_date'] = [date]
                        coll.insert_one(data['data'][y])
                    else:
                        coll.update_one({'id': data['data'][y]['id']},
                                        {'$push': {'schedule_date': date}})
            except Exception:
                pass
