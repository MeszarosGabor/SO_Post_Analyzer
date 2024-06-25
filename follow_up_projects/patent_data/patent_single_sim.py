import sys
sys.path.append("/home/debian/gabe/SO_Post_Analyzer")

import json
import time

import click

import follow_up_projects.urn_model.polyas_urn_model as polyas_urn_model


@click.command()
@click.option("--rounds", type=int)
@click.option("--bps", type=int)
@click.option("--nei", type=int)
@click.option("--noi", type=int)
@click.option("--batch", type=int)
def main(rounds, bps, nei, noi, batch):
    print("Loading count...")
    with open("results/patent_code_counts.json") as handle:
        code_counts = json.load(handle)
    print("Done")

    print("Starting simulation...")
    patent_sim = polyas_urn_model.urn_simulation_with_sqlite(
        rounds,
        base_pool_size=bps,
        new_element_increment=nei,
        new_opportunity_increment=noi,
        card_sizes=code_counts,
        batch=batch,
    )
    print("Done")
    print("Saving result to JSON...")

    payload = {k: [int(item) for item in v] for k, v in patent_sim.items()}
    
    with open(f"results/sims/patent_sim_rounds_{rounds}_bps_{bps}_nei_{nei}_noi_{noi}.json", 'w') as handle:
        json.dump(payload,  handle)
    print("Done")

if __name__ == "__main__":
    main()
