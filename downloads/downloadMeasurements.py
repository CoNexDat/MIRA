#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import requests
import pandas as pd


# define the db and collection
client = MongoClient()
db = client['yourDB']
collection = db['yourCollection']

# get the measurementIds from the provided json-file
measurements = pd.read_json('files/measurementIds.json')

# iterate over every measurement
for x in range(0, len(measurements)):
    # get measurement data from the RIPE-API
    URL = ("https://atlas.ripe.net/api/v2/measurements/"
           + str(int(measurements['msm_id'][x]))
           + "/results/?format=json")
    data = requests.get(url=URL, proxies=dict(
        https='socks5://localhost:8080')).json()
    # insert the data into the collection and catch potential errors
    try:
        collection.insert_many(data)
    except Exception:
        print('Error inserting data of Measurement: ', data[0]['msm_id'])
