import itertools
import time
import random
import sqlite3

from sqlalchemy import create_engine, Column, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import matplotlib.pyplot as plt
import more_itertools
import numpy as np
import redis
import tqdm

from redis.exceptions import BusyLoadingError
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

@profile
def multi_urn_simulation_with_sqlite(
    rounds: int,
    base_pool_count: int,
    base_pool_size: int,
    new_element_increment: int,
    new_opportunity_increment: int,
    swap_probability: float,
    cleanup: bool=True,
    card_sizes: list=None,
    poisson_mean: float=None,
    batch: int=1,
):
    Base = declarative_base()
    def create_urnsim_table_class(index):
        class UrnSimReusable(Base):
            __tablename__ = f'urnsim{index}'
            key = Column(Integer, primary_key=True)
            ball = Column(Integer)
        
        return UrnSimReusable
    
    if poisson_mean and card_sizes:
        raise ValueError("Exactly one of card_size and poisson mean should be defined!")
    if card_sizes is not None and len(card_sizes) < rounds:
        raise ValueError("If card_sizes is provided its size needs to be as much as the number of rounds requested.")
    
    # Connect to your SQLite database
    engine = create_engine('sqlite:////mnt/myssd/urn.db', echo=False)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("Flushing DB...")
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Drop all tables
    metadata.drop_all(bind=engine)

    # Commit any remaining transactions
    session.commit()
    print("... done.")

    # Create all tables based on the Base metadata
    print("recreating table...")
    urnsim_classes = []
    for i in range(base_pool_count):
        urnsim_class = create_urnsim_table_class(i)
        urnsim_classes.append(urnsim_class)
        urnsim_class.__table__.create(engine)
    print("...done.")

    pool_sizes = {i: base_pool_size for i in range(base_pool_count)}
    max_element = 0
    max_elements = {i: 0 for i in range(base_pool_count)}
    print("Filling up initial pools...")
    for urnsim_class_index in range(len(urnsim_classes)):
        for chunk in tqdm.tqdm(more_itertools.chunked(range(1, base_pool_size + 1), batch)):
            for _ in chunk:
                max_element += 1
                max_elements[urnsim_class_index] += 1
                new_e = urnsim_classes[urnsim_class_index](key=max_elements[urnsim_class_index], ball=max_element)
                session.add(new_e)
            session.commit()

    element_have_seen = set()
    pairs_have_seen = set()
    element_counts = []
    pairs_counts = []

    current_urn_index = 0
    current_urnsim_class = urnsim_classes[current_urn_index]
    print("Starting simulation...")
    for round_index in tqdm.tqdm(range(rounds)):
        number_of_items_in_post = card_sizes[round_index] if card_sizes else np.random.poisson(poisson_mean)
        elements_in_post = []
        for _ in range(number_of_items_in_post):
            # decide if we stay in the current urn or switch to another one
            if random.random() < swap_probability:
                current_urn_index = random.choice([i for i in range(len(urnsim_classes)) if i != current_urn_index])
                current_urnsim_class = urnsim_classes[current_urn_index]

            new_element_index = random.randint(1, pool_sizes[current_urn_index])
            #new_element = session.query(current_urnsim_class).filter_by(key=new_element_index).first().ball
            
            table_name = f"urnsim{current_urn_index}"
            sql_statement = text(f"SELECT ball FROM {table_name} WHERE key = :key")
            new_element = session.execute(
                sql_statement,
                {'key': new_element_index}
            ).scalar()

            # Reinforcement
            for i in range(pool_sizes[current_urn_index] + 1, pool_sizes[current_urn_index] + 1 + new_element_increment):
                new_e = current_urnsim_class(key=i, ball=new_element)
                session.add(new_e)
            pool_sizes[current_urn_index] += new_element_increment

            # Expansion via 'adjacent possible'
            if new_element not in element_have_seen:
                for i in range(pool_sizes[current_urn_index] + 1, pool_sizes[current_urn_index] + 1 + new_opportunity_increment):
                    max_element += 1
                    new_e = current_urnsim_class(key=i, ball=max_element)
                    session.add(new_e)
                pool_sizes[current_urn_index] += new_opportunity_increment
                    
            element_have_seen.add(new_element)
            elements_in_post.append(new_element)
        for element_a, element_b in itertools.combinations(elements_in_post, 2):
            canonical_name = "|".join(sorted([str(element_a), str(element_b)]))
            pairs_have_seen.add(canonical_name)

        session.commit()
        element_counts.append(len(element_have_seen))
        pairs_counts.append(len(pairs_have_seen))
    if cleanup:
        print("Flushing DB...")
        metadata = MetaData()
        metadata.reflect(bind=engine)
    
        # Drop all tables
        metadata.drop_all(bind=engine)

    return {
        "element_counts": np.array(element_counts),
        "pairs_counts": np.array(pairs_counts),
    }

import random
def main():

    card_sizes = [random.randint(1,10) for _ in range(1000)]
    total = multi_urn_simulation_with_sqlite(
    rounds=1000,
    base_pool_count=10,
    base_pool_size=100,
    new_element_increment=50,
    new_opportunity_increment=800,
    swap_probability=0.2,
    card_sizes=card_sizes,
    batch=100)
    print("Total:", total)


if __name__ == "__main__":
    main()
