#!/usr/bin/env python
# coding: utf-8


import pandas as pd


# function that transforms the json-data into a DataFrame
def main(data):
    df = pd.DataFrame(columns=['id', 'country', 'ipv4', 'prefix_v4',
                               'asn_v4', 'ipv6', 'prefix_v6', 'asn_v6'])
    for x in range(0, len(data['results'])):
        # assert that the probe has an ipv4 and ipv6 interace and is connected
        if (data['results'][x]['asn_v6'] and data['results'][x]['asn_v4']
                and data['results'][x]['status']['name'] == 'Connected'):
            df2 = pd.DataFrame({'id': [data['results'][x]['id']],
                                'country': [data['results'][x]['country_code']],
                                'ipv4': [data['results'][x]['address_v4']],
                                'prefix_v4': [data['results'][x]['prefix_v4']],
                                'asn_v4': [data['results'][x]['asn_v4']],
                                'ipv6': [data['results'][x]['address_v6']],
                                'prefix_v6': [data['results'][x]['prefix_v6']],
                                'asn_v6': [data['results'][x]['asn_v6']]})
            df = df.append(df2, ignore_index=True, sort=True)
    return df
