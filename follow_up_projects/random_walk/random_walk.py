import itertools
import time
import typing

import networkx as nx
import random
import numpy as np
from tqdm import tqdm


def create_graph(edges):
    """
    Create a graph with given edges and initialize all edge weights to 1.
    :param edges: List of tuples representing edges (u, v).
    :return: A NetworkX graph with initialized edge weights.
    """
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=1)
    return G


def create_complete_graph(vertices):
    G = nx.Graph()
    print(f"Creating edges for {len(vertices)} nodes, that is, {len(vertices) * (len(vertices) - 1) // 2} edges")
    for edge in itertools.combinations(vertices, 2):
        G.add_edge(edge[0], edge[1], weight=1)
    return G


def weighted_random_choice(choices, weights):
    """
    Select a random element from the list 'choices' with the given 'weights'.
    :param choices: List of elements to choose from.
    :param weights: List of weights corresponding to the elements in 'choices'.
    :return: A randomly selected element from 'choices' based on 'weights'.
    """
    total = sum(weights)
    cum_weights = np.cumsum(weights)
    rnd = random.random() * total
    return choices[np.searchsorted(cum_weights, rnd)]


def random_walk(G, start_node, steps, weight_update):
    """
    Perform a random walk on the graph, updating the edge weights.
    :param G: The graph.
    :param start_node: The starting node of the walk.
    :param steps: The number of steps in the random walk.
    :param x: The increment to the edge weight after each traversal.
    :return: List of nodes visited in the random walk.
    """
    current_node = start_node
    walk = [current_node]

    for _ in tqdm(range(steps)):
        neighbors = list(G.neighbors(current_node))
        if not neighbors:
            break
        # Get the weights of the edges to the neighbors
        weights = [G[current_node][neighbor]['weight'] for neighbor in neighbors]
        # Choose the next node based on the weights
        next_node = weighted_random_choice(neighbors, weights)
        # Update the weight of the traversed edge
        G[current_node][next_node]['weight'] += weight_update
        # Move to the next node
        current_node = next_node
        walk.append(current_node)

    return walk



def convert_nx_graph_to_primitive_neighbors_dict(G: nx.Graph):
    return {node: list(G.neighbors(node)) for node in G.nodes()}


def random_walk_edge_reinforcement(
    neighbors: typing.Dict[int, typing.List],
    rounds: int,
    start_index: typing.Union[int, None]=None,
    initial_weights: int=1,
    reinforcement_weight: int=0,
    return_neighbors: bool=False,
    with_logging: bool=True):
    """
    Random walk implementation using primitive structures only (no networkx; aiming for fast random selections).
    We use random access indexes of the neighbor lists to quickly select new nodes.
    We also reinforce edges by listing the neighbors multiple times (hence reinforcement weight must be an integer).
    """
    t0 = time.time()
    print("Setup...")
    act_node = start_index if start_index is not None else random.choice(neighbors)
    walk = [act_node]

    if initial_weights > 1:
        for node, neighbor_list in neighbors.items():
            neighbors[node] = neighbor_list * initial_weights
    t1 = time.time()
    if with_logging:
        print(f"...Done. Took {round((t1 - t0), 1)} seconds. Starting Rounds...")

    t0 = time.time()
    for round_index in range(1, rounds + 1):
        if with_logging and round_index % 100 == 0:
            print(f"Doing round #{round_index}")
        old_node, act_node = act_node, random.choice(neighbors[act_node])
        walk.append(act_node)

        # reinforcement
        neighbors[old_node].extend([act_node for _ in range(reinforcement_weight)])
        neighbors[act_node].extend([old_node for _ in range(reinforcement_weight)])
    t1 = time.time()
    if with_logging:
        print(f"...Done. Took {round((t1 - t0), 1)} seconds.")
    if return_neighbors:
        return {
            "walk": walk,
            "neighbors": neighbors,
        }
    return {"walk": walk}