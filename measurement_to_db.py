#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import requests
import pandas as pd


def main(date, measurements):
    # define the db and collection
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['traceroutes']

    for x in range(0, len(measurements)):
        # get measurement-data from db and start Thread to insert it into DB
        URL = ("https://atlas.ripe.net/api/v2/measurements/"
               + str(int(measurements['measurements'][x]))
               + "/results/?format=json")
        data = requests.get(url=URL, proxies=dict(
                                https='socks5://localhost:8080')).json()
        for x in range(0, len(data)):
            data[x]['schedule_date'] = date

        # insert the data into the collection and catch potential errors
        try:
            coll.insert_many(data)
        except Exception:
            print('Error inserting data of Measurement: ', data[0]['msm_id'])
