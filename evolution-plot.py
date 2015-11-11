#!/usr/bin/env python3

"""Plots the evolution of an algorithm(s) by defining the
relationships between them.
"""

import os
from collections import defaultdict
from functools import partial
import argparse
from textwrap import wrap
import yaml
from graphviz import Digraph

# TODO: remove
from pprint import pprint

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
STYLE_FILE = os.path.join(__location__, 'format.yml')

def compose(*a):
    def composed(f, g, *args, **kwargs):
        return f(g(*args, **kwargs))
    try:
        return partial(composed, a[0], compose(*a[1:]))
    except:
        return a[0]


def load_data(file):
    with open(file, encoding='utf-8') as f:
        return yaml.safe_load(f)


def make_multi_font_label(labels, attributes, widths):
    def ensure_string(maybe_string):
        return ' ' if not maybe_string else str(maybe_string)
    labels = map(ensure_string, labels)

    return '< {} >'.format('<BR/>'.join(
        '<FONT {}>{} </FONT>'.format(
            ' '.join('{}="{}"'.format(k, v) for k, v in attr.items()),
            '<BR/>'.join(wrap(label, width)))
        for label, attr, width in zip(labels, attributes, widths)))


def by_year_subgraph_constructor():
    subgraph = Digraph()
    subgraph.body.append('rank=same')
    return subgraph


def add_edges(g, node, relation, styles):
    if relation in node and node[relation]:
        name = node['short name']
        for link_obj in node[relation]:
            # link might be listed as string or as only key of a dict
            try:
                link = ''.join(list(link_obj.keys())) # if dict
            except:
                link = link_obj

            # link name may or may not be defined
            try:
                link_name = data[link]['short name']
            except:
                link_name = link
                g.node(link_name, **styles['unknown nodes'])

            g.edge(link_name, name, **styles[relation])


def generate_evolution_plot(data):
    g = Digraph(format='png')
    styles = load_data(STYLE_FILE)

    # apply global graph styles
    g.body.extend('{}={}'.format(k, v)
                  for k, v in styles['graph'].items())

    # plot nodes
    subgraphs = defaultdict(by_year_subgraph_constructor)
    for node in data.values():
        name = node['short name']
        label = make_multi_font_label(*zip(*(
            (name,                styles['node name font'],
             styles['node name width']),
            (node['title'],       styles['node title font'],
             styles['node title width']),
            (node['authors'],     styles['node authors font'],
             styles['node authors width']),
            (node['description'], styles['node description font'],
             styles['node description width']))))
        subgraphs[node['year']].node(name, label, **styles['nodes'])

    # plot edges
    for id, node in data.items():
        name = node['short name']

        add_edges(g, node, 'develops on', styles)
        add_edges(g, node, 'similar to', styles)

    # plot year legend
    years = sorted(list(subgraphs.keys()))
    for year, graph in subgraphs.items():
        graph.node(str(year), **styles['year nodes'])
    for first, second in zip(years, years[1:]):
        g.edge(str(first), str(second), **styles['year edges'])

    for graph in subgraphs.values():
        g.subgraph(graph)

    g.render('img')
    return g


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot algorithm evolution.')
    parser.add_argument('data', help='Yaml file containing data.')
    args = parser.parse_args()
    data_file = args.data
    data = load_data(data_file)
    graph = generate_evolution_plot(data)
    print(str(str(graph).encode(
        'ascii', errors='backslashreplace').decode()))
