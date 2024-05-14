import itertools
import time
import random

import matplotlib.pyplot as plt
import more_itertools
import numpy as np
import redis
import tqdm

from redis.exceptions import BusyLoadingError
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type



def urn_simulation(
    rounds: int,
    base_pool_size: int,
    new_element_increment: int,
    new_opportunity_increment: int,
    card_sizes: list=None,
    poisson_mean: float=None,
):
    if poisson_mean and card_sizes:
        raise ValueError("Exactly one of card_size and poisson mean should be defined!")
    if card_sizes is not None and len(card_sizes) < rounds:
        raise ValueError("If card_sizes is provided its size needs to be as much as the number of rounds requested.")
    base_pool = list(range(base_pool_size))
    element_have_seen = set()
    pairs_have_seen = set()
    element_counts = []
    pairs_counts = []
    
    for round_index in tqdm.tqdm(range(rounds)):
        number_of_items_in_post = card_sizes[round_index] if card_sizes else np.random.poisson(poisson_mean)
        elements_in_post = []
        for _ in range(number_of_items_in_post):
            new_element = random.choice(base_pool)
            base_pool.extend([new_element for _ in range(new_element_increment)])
            if new_element not in element_have_seen:
                base_pool.extend([base_pool[-1] + i for i in range(1, new_opportunity_increment + 1)])
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


@retry(
        wait=wait_fixed(300),
        stop=stop_after_attempt(10),
        retry=retry_if_exception_type(BusyLoadingError)
    )
def redis_flushdb(r_url):
    try:
        r_url.flushdb()
    except BusyLoadingError:
        print("Redis is busy, come back on Monday...")
        raise


@retry(
        wait=wait_fixed(300),
        stop=stop_after_attempt(10),
        retry=retry_if_exception_type(BusyLoadingError)
    )
def redis_get(r_url, key):
    try:
        return r_url.get(key)
    except BusyLoadingError:
        print("Redis is busy, come back on Monday...")
        raise


@retry(
        wait=wait_fixed(300),
        stop=stop_after_attempt(10),
        retry=retry_if_exception_type(BusyLoadingError)
    )
def redis_set(rp_url, key, value):
    try:
        rp_url.set(key, value)
    except BusyLoadingError:
        print("Redis is busy, come back on Monday...")
        raise


@retry(
        wait=wait_fixed(300),
        stop=stop_after_attempt(10),
        retry=retry_if_exception_type(BusyLoadingError)
    )
def redis_execute(rp_url):
    try:
        rp_url.execute()
    except BusyLoadingError:
        print("Redis is busy, come back on Monday...")
        raise


def urn_simulation_with_redis(
    rounds: int,
    base_pool_size: int,
    new_element_increment: int,
    new_opportunity_increment: int,
    card_sizes: list=None,
    poisson_mean: float=None,
):
    if poisson_mean and card_sizes:
        raise ValueError("Exactly one of card_size and poisson mean should be defined!")
    if card_sizes is not None and len(card_sizes) < rounds:
        raise ValueError("If card_sizes is provided its size needs to be as much as the number of rounds requested.")
    
    r_url = redis.Redis(host="127.0.0.1", port=6379, db=10, decode_responses=True)
    print("Flushing Redis...")
    redis_flushdb(r_url)  # remove previous urn model
    print("... done.")
    rp_url = r_url.pipeline()
    
    pool_size = base_pool_size
    max_element = base_pool_size
    print("Filling up initial pool...")
    for chunk in tqdm.tqdm(more_itertools.chunked(range(1, base_pool_size + 1), 1000)):
        for i in chunk:
            redis_set(rp_url, i, i)
        redis_execute(rp_url)
    element_have_seen = set()
    pairs_have_seen = set()
    element_counts = []
    pairs_counts = []

    for round_index in tqdm.tqdm(range(rounds)):
        number_of_items_in_post = card_sizes[round_index] if card_sizes else np.random.poisson(poisson_mean)
        elements_in_post = []
        for _ in range(number_of_items_in_post):
            new_element = redis_get(r_url, random.randint(1, pool_size))
            for i in range(pool_size + 1, pool_size + 1 + new_element_increment):
                redis_set(rp_url, i, new_element)
            pool_size += new_element_increment
            if new_element not in element_have_seen:
                for i in range(pool_size + 1, pool_size + 1 + new_opportunity_increment):
                    max_element += 1
                    redis_set(rp_url, i, max_element)
            redis_execute(rp_url)
                    
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

