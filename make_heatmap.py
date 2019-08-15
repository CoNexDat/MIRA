#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import graphic_to_db


def main(data, version, date):
    # make heatmap
    figurename = date + '_heatmap_v' + str(version) + '.png'
    plt.clf()
    ax = plt.axes()
    g = sns.heatmap(data, cmap='nipy_spectral', ax=ax, vmin=0, vmax=300,
                    xticklabels=True, yticklabels=True)
    g.set_title('Median(ms) of RTTs by country, IPv' + str(version)
                 + ' (as of '
                 + datetime.strptime(date, '%Y%m%d').strftime("%d %b %Y")
                 + ')')
    g.get_figure().savefig('./graphs/' + figurename)

    # save heatmap to the db
    graphic_to_db.main(date, figurename)
