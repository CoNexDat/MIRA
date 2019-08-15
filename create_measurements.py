#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from pymongo import MongoClient
import time
from ripe.atlas.cousteau import AtlasStopRequest
from threading import Thread
import execute_POST_req
import measurement_to_db


# method to create a measurement from every probe to every AS
def main(date, version, probes, asns, repetition, concurrent, description,
         protocol, packets, first_hop, max_hops, paris, bill_to, api_key):
    # define the date and db

    # create empty DataFrame for API-Responses
    measurements = pd.DataFrame()

    # create 100 measurements (limit for concurrent measurements)
    # until every target was selected
    for x in range(0, int(repetition*len(asns)/concurrent)+1):
        for y in range(0, concurrent):
            # check if end of list is reached
            if (y+x*concurrent)/repetition < len(asns):
                # create measurement
                execute_POST_req.main(
                    str(asns['ipv' + str(version)][int(
                        (y+x*concurrent)/repetition)]),
                    len(probes), ",".join(map(str, probes['id'])), version,
                    description, protocol, packets, first_hop, max_hops,
                    paris, bill_to, api_key)
                # read the API-Response into the DataFrame
                apiResponse = pd.read_json('ripeApiResponse.txt')
                if 'measurements' in apiResponse:
                    measurements = measurements.append(apiResponse,
                                                       ignore_index=True,
                                                       sort=True)
            else:
                break

        # wait until measurements are done and stop them to safe RIPE-credits
        # and write them into the db
        time.sleep(1800)
        for x in range(0, len(measurements)):
            # stop measurement
            atlas_request = AtlasStopRequest(msm_id=measurements[
                'measurements'][x], key=api_key, proxies=dict(
                https='socks5://localhost:8080'))
            (is_success, response) = atlas_request.create()

        # pass measurement ids to the script to save them to the db
        Thread(target=measurement_to_db.main,
               args=(date, measurements)).start()

        # empty DataFrame to prevent redundancy
        measurements = pd.DataFrame()
