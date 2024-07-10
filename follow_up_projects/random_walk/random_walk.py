import itertools
import random
import time
import typing

import networkx as nx
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


def random_walk_edge_reinforcement_and_triggering(
    neighbors: typing.Dict[int, typing.List],
    rounds: int,
    start_index: typing.Union[int, None]=None,
    initial_weights: int=1,
    edge_reinforcement_weight: int=0,
    node_reinforcement_new_link_count: int=0,
    expansion_new_node_count: int=0,
    try_count_hard_limit: int=1000,
    return_neighbors: bool=False,
    with_logging: bool=True):
    """
    Random walk implementation using primitive structures only (no networkx; aiming for fast random selections).
    We use random access indexes of the neighbor lists to quickly select new nodes.
    We also reinforce edges by listing the neighbors multiple times (hence reinforcement weight must be an integer).
    """
    def edge_canonical_repr(node_a, node_b):
        return tuple(sorted([node_a, node_b]))

    t0 = time.time()
    print("Setup...")
    have_seen_edges = set()
    for node, node_neighbors in neighbors.items():
        for neighbor in node_neighbors:
            have_seen_edges.add(edge_canonical_repr(node, neighbor))

    have_walked_edges = set()
    max_node = max(neighbors)
    act_node = start_index if start_index is not None else random.choice(neighbors)
    have_walked_nodes = set([act_node])
    walk = [act_node]

    if initial_weights > 1:
        for node, neighbor_list in neighbors.items():
            neighbors[node] = neighbor_list * initial_weights
    t1 = time.time()
    if with_logging:
        print(f"...Done. Took {round((t1 - t0), 1)} seconds. Starting Rounds...")

    t0 = time.time()
    for round_index in range(1, rounds + 1):
        if with_logging:
            print(f"Doing round #{round_index}. Act node is {act_node}")
        old_node, act_node = act_node, random.choice(neighbors[act_node])

        # edge reinforcement - this should happen at every move
        neighbors[old_node].extend([act_node for _ in range(edge_reinforcement_weight)])
        neighbors[act_node].extend([old_node for _ in range(edge_reinforcement_weight)])

        # node reinforcement - only apply at the end nodes of a newly explored link.
        if edge_canonical_repr(old_node, act_node) not in have_walked_edges:
            # collect randomly chosen non-links from act_node with sampling
            non_neighbors_selected = set()
            try_count = 0
            while (
                len(non_neighbors_selected) < node_reinforcement_new_link_count and 
                try_count < try_count_hard_limit
            ):
                try_count += 1
                candidate = random.randint(1, max_node)
                if (
                    candidate == act_node or
                    edge_canonical_repr(candidate, act_node) in have_seen_edges
                ):
                    continue
                non_neighbors_selected.add(candidate)
            if with_logging:
                print(
                    f"Node reinforcement ended after {try_count} tries. "
                    f"Collected {len(non_neighbors_selected)} non-neighbors ({non_neighbors_selected}) out of {node_reinforcement_new_link_count}"
                )
            for non_ns in non_neighbors_selected:
                neighbors[act_node].append(non_ns)
                neighbors[non_ns].append(act_node)
                have_seen_edges.add(edge_canonical_repr(non_ns, act_node))

        # expansion - only when a new node is visited
        if act_node not in have_walked_nodes:
            for new_born_node in range(max_node + 1, max_node + expansion_new_node_count + 1):
                neighbors[act_node].append(new_born_node)
                neighbors[new_born_node] = [act_node]
            max_node += expansion_new_node_count
            if with_logging:
                print(f"Act node {act_node} spawned {expansion_new_node_count} new nodes. Max node is now: {max_node}")

        # updates
        walk.append(act_node)
        have_walked_edges.add(edge_canonical_repr(old_node, act_node))
        have_walked_nodes.add(act_node)
        
    t1 = time.time()
    if with_logging:
        print(f"...Done. Took {round((t1 - t0), 1)} seconds.")
    if return_neighbors:
        return {
            "walk": walk,
            "neighbors": neighbors,
        }
    return {"walk": walk}