#!/usr/bin/env python
# coding: utf-8


from datetime import datetime, timedelta
import json
import subprocess


# function to call script to make an API-Request to RIPE-Atlas
# and pass the data-payload
def main(target, requested, value, version, description, protocol,
         packets, first_hop, max_hops, paris, bill_to, api_key):
    # request-data for a traceroute according to RIPE definitions

    time = datetime.utcnow() + timedelta(minutes=61)
    data = {
        "definitions": [
            {
                "target": target,
                "af": version,
                "description": description,
                "protocol": protocol,
                "packets": packets,
                "size": 48,
                "first_hop": first_hop,
                "max_hops": max_hops,
                "paris": paris,
                "interval": 3600,
                "type": "traceroute"
            }
        ],
        "probes": [
            {
                   "value": value,
                   "type": "probes",
                   "requested": requested
            }
        ],
        "is_oneoff": False,

        "stop_time": int(time.timestamp()),
        "bill_to": bill_to
    }
    # pass data into post-request-script and execute it
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    # api_key='3787ffea-1b93-4b17-9bac-38674b8b9af2'
    subprocess.call(['./ripeApiRequest', api_key])
