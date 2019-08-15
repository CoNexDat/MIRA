#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
from gridfs import GridFS


def main(date, figurename):
    # define the db
    client = MongoClient()
    db = client['conexdat-db']
    coll = db['dates']
    fs = GridFS(db)

    # save graphic to the db
    try:
        img = open('graphs/' + figurename, mode='rb')
        fsImg = fs.put(img, filename=figurename)
        coll.update_one({'date': date}, {'$set': {figurename[9:-4]: fsImg}})
    except Exception:
        print(figurename + ' not found')
