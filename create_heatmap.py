#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import seaborn as sns
import get_traceroute_data
import make_heatmap


# function to create a heatmap of the Traceroute-Data by Country:
def main(date):
    # get IPv4 Traceroute-Data
    dataV4 = get_traceroute_data.main(4, date)

    # reorder data using seaborn hierarchical clustering
    cg = sns.clustermap(dataV4, method='single', metric='euclidean')

    rows = cg.dendrogram_row.reordered_ind
    rows_df = dataV4.index.values
    rows_df_new = []
    for x in range(0, len(rows_df)):
        rows_df_new.append(rows_df[rows[x]])
    dataV4 = dataV4.reindex(rows_df_new, axis=0)

    cols = cg.dendrogram_col.reordered_ind
    cols_df = list(dataV4)
    cols_df_new = []
    for x in range(0, len(cols_df)):
        cols_df_new.append(cols_df[cols[x]])
    dataV4 = dataV4.reindex(cols_df_new, axis=1)

    # pass IPv4 data to make and save the IPv4 heatmap
    make_heatmap.main(dataV4, 4, date)

    # get IPv6 data and reindex it
    dataV6 = get_traceroute_data.main(6, date)
    dataV6 = dataV6.reindex(rows_df_new, axis=0)
    dataV6 = dataV6.reindex(cols_df_new, axis=1)

    # pass IPv6 data to make and save the IPv6 heatmap
    make_heatmap.main(dataV6, 6, date)
