import time

import click
import json
import redis

import polyas_urn_model_ram_optimized as pumro


@click.command()
@click.option("--epochs", type=int, default=1)
@click.option("--rounds", type=int, default=0)
@click.option("--bps", type=int, default=1)
@click.option("--nei", type=int)
@click.option("--noi", type=int)
def main(epochs, rounds, bps, nei, noi):
    sims = redis.Redis(host="127.0.0.1", port=6379, db=4, decode_responses=True)

    with open("patent_code_counts.json") as handle:
        code_counts = json.load(handle)
    with open("patent_novelties.json") as handle:
        temp = json.load(handle)
        novelty_count = temp["novelty_count"]
        novelty_pair_count = temp["novelty_pair_count"]
    if not rounds:
        rounds = len(novelty_pair_count)

    t0 = time.time()
    label = f"rounds_{rounds}_bps_{bps}_nei_{nei}_noi_{noi}"
    print(f"Running sim {label}")
    sim = pumro.run_simulation(
        epochs=epochs,
        rounds=rounds,
        base_pool_size=bps,
        new_element_increment=nei,
        new_opportunity_increment=noi,
        card_sizes = code_counts,
    )
    t1 = time.time()
    print(f"\tsimulation took {round(t1-t0)} seconds.")

    sim_str = json.dumps(sim)
    sims.set(label, sim_str)
    t2 = time.time()
    print(f"\tpersistence took {round(t2-t1)} seconds.")
    print("DONE")


if __name__ == "__main__":
    main()

