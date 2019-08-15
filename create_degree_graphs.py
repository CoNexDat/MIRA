#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import collections
from datetime import datetime
import graphic_to_db


def main(version, date, df):
    # create NetworkX Graph
    G = nx.Graph()
    row_iterator = df.iterrows()
    for i, row in row_iterator:
        G.add_edge(row.asn1, row.asn2)

    # calculate the metrics
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    degree = pd.DataFrame(G.degree(), columns=['node', 'degree'])
    avg_neighbor = pd.DataFrame(nx.average_neighbor_degree(G).items(),
                                columns=['node', 'avgnd'])
    cluster = pd.DataFrame(nx.clustering(G).items(), columns=['node',
                                                              'cluster'])
    df = degree.merge(avg_neighbor, on='node').merge(cluster, on='node')
    df = df.groupby('degree').sum(axis=1).drop(columns=['node'])

    plt_neighbor = pd.DataFrame(columns=['deg', 'avgnd'])
    plt_cluster = pd.DataFrame(columns=['deg', 'cluster'])
    for x in range(0, len(deg)):
        plt_neighbor = plt_neighbor.append(
            pd.Series({'deg': deg[x],
                       'avgnd': df['avgnd'][deg[x]]/cnt[x]}),
            ignore_index=True)
        plt_cluster = plt_cluster.append(
            pd.Series({'deg': deg[x],
                       'cluster': df['cluster'][deg[x]]/cnt[x]}),
            ignore_index=True)

    # create and save the graphics
    # degree distribution
    figurename = date + '_degree_distribution_v' + str(version) + '.png'
    fig, ax = plt.subplots()
    plt.bar(deg, cnt)
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_title('IPv' + str(version) + ' Degree Distribution (as of '
                 + datetime.strptime(date, '%Y%m%d').strftime("%d %b %Y")
                 + ')')
    fig.savefig('./graphs/' + figurename)
    graphic_to_db.main(date, figurename)

    # average neighbor degree
    figurename = date + '_avg_neighbor_v' + str(version) + '.png'
    fig, ax = plt.subplots()
    plt.bar(plt_neighbor['deg'], plt_neighbor['avgnd'])
    plt.ylabel("Average Neighbor Degree")
    plt.xlabel("Degree")
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_title('IPv' + str(version) + ' Average Neighbor Degree (as of '
                 + datetime.strptime(date, '%Y%m%d').strftime("%d %b %Y") +
                 ')')
    fig.savefig('./graphs/' + figurename)
    graphic_to_db.main(date, figurename)

    # clustering coefficient
    figurename = date + '_cluster_v' + str(version) + '.png'
    fig, ax = plt.subplots()
    plt.bar(plt_cluster['deg'], plt_cluster['cluster'])
    plt.ylabel("Cluster")
    plt.xlabel("Degree")
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_title('IPv' + str(version) + ' Clustering Coefficient (as of '
                 + datetime.strptime(date, '%Y%m%d').strftime("%d %b %Y")
                 + ')')
    fig.savefig('./graphs/' + figurename)
    graphic_to_db.main(date, figurename)
