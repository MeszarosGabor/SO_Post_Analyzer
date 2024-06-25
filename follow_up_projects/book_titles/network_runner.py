import sys
sys.path.append("/home/debian/gabe/SO_Post_Analyzer")


import collections
import itertools
import json

import click
import tqdm
from follow_up_projects.random_walk import random_walk as rw


@click.command()
@click.option("-r", "--reinforcement", type=float)
@click.option("--complete", is_flag=True, show_default=True, default=False)
def main(reinforcement, complete):
    with open("word_pair_have_seen.json") as handle:
        word_pair_have_seen = set(json.load(handle))
    with open("sorted_titles.json") as handle:
        sorted_titles = json.load(handle)

    print(f"Working on reinforcement {reinforcement}, complete graph: {bool(complete)}")
    edges = [item.split("|") for item in word_pair_have_seen]
    if complete:
        vertices = set([item for edge in edges for item in edge])
        word_graph = rw.create_complete_graph(vertices)
    else:
        word_graph = rw.create_graph(edges)
    
    title_lengths = [len(title) for title in sorted_titles]

    walk = rw.random_walk(word_graph, sorted_titles[0][1][0], sum(title_lengths) - 1, reinforcement)
    walk_popable = collections.deque(walk)

    words_have_seen = set()
    word_pairs_have_seen = set()
    unique_word_count = []
    unique_pair_count = []
    for title_length in tqdm.tqdm(title_lengths):
        card = [walk_popable.popleft() for _ in range(title_length)]
        for item in card:
            words_have_seen.add(item)
        for pair in itertools.combinations(card, 2):
            word_pairs_have_seen.add(pair)
        unique_word_count.append(len(words_have_seen))
        unique_pair_count.append(len(word_pairs_have_seen))

    with open(f"network_novelty_sim_r_{reinforcement}{'_complete' if complete else ''}.json", "w") as handle:
        json.dump({
            "unique_word_count": unique_word_count,
            "unique_pair_count": unique_pair_count,
        }, handle)


if __name__ == "__main__":
    main()