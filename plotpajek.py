#!/usr/bin/env python

"""Plots the graph in Pajek format

It uses networkx for the plotting, which in turn is replied upon the matplotlib
for the actual drawing engine.

"""

import sys

import networkx as nx
import matplotlib.pyplot as plt


def main():

    """The main function"""

    try:
        file_name = sys.argv[1]
    except IndexError:
        print "Input file not given!"
        raise
    base_name = file_name.split('.')[0]

    net = nx.read_pajek(file_name)
    nx.draw_graphviz(net, with_labels=True)
    plt.draw()
    plt.savefig(base_name + '.png')


if __name__ == '__main__':
    main()
