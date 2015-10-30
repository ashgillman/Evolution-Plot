"""Plots the evolution of an algorithm(s) by defining the
relationships between them.
"""
import os
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
    with open(file) as f:
      return yaml.safe_load(f)


def make_multi_font_label(labels, attributes, width=30):
    def ensure_string(maybe_string):
        return '' if maybe_string is None else str(maybe_string)
    labels = map(ensure_string, labels)

    return '< {} >'.format('<BR/>'.join(
        '<FONT {}>{}</FONT>'.format(
            ' '.join('{}="{}"'.format(k, v) for k, v in attr.items()),
            '<BR/>'.join(wrap(label, width)))
        for label, attr in zip(labels, attributes)))


def generate_evolution_plot(data):
    g = Digraph(format='png')
    styles = load_data(STYLE_FILE)

    # apply graph styles
    g.body.extend('{}={}'.format(k, v)
                  for k, v in styles['graph'].items())

    # plot years and all nodes (by year)
    unique = compose(sorted, list, set)
    years = unique([node['year'] for node in data.values()])
    years = list(map(str, years)) # stringify
    for year in years:
        year_g = Digraph()
        year_g.body.append('rank=same')

        year_g.node(year, **styles['year nodes'])

        year_nodes = [node for node in data.values()
                      if str(node['year']) == year]

        for node in year_nodes:
            name = node['short name']
            label = make_multi_font_label(*zip(*(
                (name,                {'POINT-SIZE': 20}),
                (node['authors'],     {'POINT-SIZE':  8, 'COLOR': 'red'}),
                (node['description'], {'POINT-SIZE': 10}))))
            year_g.node(name, label, **styles['nodes'])

        g.subgraph(year_g)

    # year edges
    for first, second in zip(years, years[1:]):
        g.edge(first, second, **styles['year edges'])

    # plot edges
    for id, node in data.items():
        name = node['short name']

        # plot node edges
        def add_edges(node, relation):
            if relation in node and node[relation]:
                for link_obj in node[relation]:
                    try:
                        link = ''.join(list(link_obj.keys())) # if dict
                    except:
                        link = link_obj
                    try:
                        link_name = data[link]['short name']
                    except:
                        link_name = link
                    print(link_name)
                    g.edge(link_name, name, **styles[relation])

        add_edges(node, 'develops on')
        add_edges(node, 'similar to')
    g.render('img')
    return g


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot algorithm evolution.')
    parser.add_argument('data', help='Yaml file containing data.')
    args = parser.parse_args()
    data_file = args.data
    data = load_data(data_file)
    print(generate_evolution_plot(data))
