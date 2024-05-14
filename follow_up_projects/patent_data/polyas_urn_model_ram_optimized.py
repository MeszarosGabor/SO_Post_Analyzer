import collections
import bisect
import itertools
import random

import numpy as np
import tqdm


def urn_simulation(
    rounds: int,
    base_pool_size: int,
    new_element_increment: int,
    new_opportunity_increment: int,
    card_sizes: list=None,
    poisson_mean: float=None,
):
    if poisson_mean and card_sizes or poisson_mean is None and card_sizes is None:
        raise ValueError("Exactly one of card_size and poisson mean should be defined!")
    if card_sizes is not None and len(card_sizes) < rounds:
        raise ValueError("If card_sizes is provided its size needs to be as much as the number of rounds requested.")
    base_pool = collections.defaultdict(int)
    for index in range(base_pool_size):
        base_pool[index] += 1
    max_pool_element = base_pool_size - 1
    element_have_seen = set()
    pairs_have_seen = set()
    element_counts = []
    pairs_counts = []

    for round_index in tqdm.tqdm(range(rounds)):
        number_of_items_in_post = card_sizes[round_index] if card_sizes else np.random.poisson(poisson_mean)
        elements_in_post = []
        for _ in range(number_of_items_in_post):
            choices, weights = zip(*base_pool.items())
            cumdist = list(itertools.accumulate(weights))
            x = random.random() * cumdist[-1]
            new_element = choices[bisect.bisect(cumdist, x)]    

            if base_pool[new_element] == 1:
                for i in range(max_pool_element + 1, max_pool_element + 1 + new_opportunity_increment):
                    base_pool[i] += 1
                max_pool_element += new_opportunity_increment
            base_pool[new_element] += new_element_increment

            element_have_seen.add(new_element)
            elements_in_post.append(new_element)
        for element_a, element_b in itertools.combinations(elements_in_post, 2):
           canonical_name = "|".join(sorted([str(element_a), str(element_b)]))
           pairs_have_seen.add(canonical_name)
        element_counts.append(len(element_have_seen))
        pairs_counts.append(len(pairs_have_seen))
    
    return {
        "element_counts": np.array(element_counts),
        "pairs_counts": np.array(pairs_counts),
    }


def run_simulation(
    epochs: int,
    rounds: int,
    base_pool_size: int,
    new_element_increment: int,
    new_opportunity_increment: int, 
    card_sizes: list=None,
    poisson_mean: float=None,
):
    if poisson_mean and card_sizes:
        raise ValueError("Exactly one of card_sizes and poisson mean should be defined!")
    if card_sizes is not None and len(card_sizes) < rounds:
        raise ValueError("If card_sizes is provided its size needs to be as much as the number of rounds requested.")
    
    results =  {
        "element_counts": np.zeros(rounds),
        "pairs_counts": np.zeros(rounds),
    }
    for _ in range(epochs):
        new_sim = urn_simulation(
            rounds, base_pool_size, new_element_increment, new_opportunity_increment, card_sizes, poisson_mean)
        results["element_counts"] += new_sim["element_counts"]
        results["pairs_counts"] += new_sim["pairs_counts"]
    results["element_counts"] /= epochs
    results["pairs_counts"] /= epochs
    
    return {
        "element_counts": list(results["element_counts"]),
        "pairs_counts": list(results["pairs_counts"]),
    }

