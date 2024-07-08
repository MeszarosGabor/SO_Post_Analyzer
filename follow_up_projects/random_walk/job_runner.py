import math

import click
import networkx as nx

import random_walk as rw


@click.command()
@click.option("-n", "--nodes", type=int)
@click.option("-r", "--rounds", type=int)
def main(nodes, rounds):
    p = math.log(nodes) * 2 / nodes 
    G = nx.erdos_renyi_graph(nodes, p)
    neighbors = rw.convert_nx_graph_to_primitive_neighbors_dict(G)
    
    walk = rw.random_walk_edge_reinforcement(
        neighbors,
        rounds=rounds, start_index=0, initial_weights=1, reinforcement_weight=1, return_neighbors=False)
    print(walk)

if __name__ == "__main__":
    main()
