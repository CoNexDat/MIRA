#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import pandas as pd
import subprocess
from gridfs import GridFS


# function to create a network-map of the AS-data using LaNet-vi
def main(version, date, df):
    # define the db and pyasn file
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['dates']
    fs = GridFS(db)

    # convert DataFrame to csv-file for LaNet to work with
    csv_name = date + '_edgelist_v' + str(version) + '.csv'
    df.to_csv('edgelists/' + csv_name, index=False, header=False, sep=' ')

    # run LaNet-vi
    subprocess.call(['programs/LaNet-vi_3.0.1/lanet', '-input',
                     'edgelists/' + csv_name])

    # open and save result to the db
    imgName = csv_name[:-4] + '_col_b_800x600POV.png'
    try:
        lanetImg = open(imgName, 'rb')
        lanet = fs.put(lanetImg, filename=csv_name[:-4] + '.png')
        coll.update_one({'date': date},
                        {'$set': {'lanet_v' + str(version): lanet}})
    except Exception:
        print('Img not found')
