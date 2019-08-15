#!/usr/bin/env python
# coding: utf-8


from datetime import datetime
import requests
from bs4 import BeautifulSoup
import zlib


# function to get the current routeviews-data from CAIDA
# and transform into pyasn-data
def main(date):
    # set URL for both IP-Versions with the current month
    URLv4 = ('http://data.caida.org/datasets/routing/routeviews-prefix2as/'
             + datetime.today().strftime("%Y/%m/"))
    URLv6 = ('http://data.caida.org/datasets/routing/routeviews6-prefix2as/'
             + datetime.today().strftime("%Y/%m/"))

    # get page of the current month, fetch the the last file
    # and transform into pyasn-data
    def get_current_file(URL, version):
        page = requests.get(URL).text
        soup = BeautifulSoup(page, 'html.parser')
        path_last_file = soup.find_all('a')[-1].get_text()
        file_path = (path_last_file[-23:-15] + '-routeviews-rv'
                     + str(version) + '.pfx2as.gz')
        r = requests.get(URL + path_last_file, stream=True)
        if r.status_code == 200:
            data = zlib.decompress(r.content, zlib.MAX_WBITS | 32)
            with open('routeviews/' + file_path, 'wb') as f:
                f.write(data)
        with open('routeviews/' + file_path, 'r') as f:
            with open('ipasns/' + date + '-ipasn-v' + str(version)
                      + '.dat', 'w') as g:
                for line in f:
                    pfix, mask, asn = str(line).split('\t')
                    parsed_line = ('{pfix}/{mask}\t{asn}'
                                   .format(pfix=pfix, mask=mask, asn=asn))
                    g.write(parsed_line)

    # get both files and safe them
    get_current_file(URLv4, 4)
    get_current_file(URLv6, 6)
