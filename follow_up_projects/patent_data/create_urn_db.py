from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UrnSim(Base):
    __tablename__ = 'urnsim'

    key = Column(Integer, primary_key=True)  # Primary key column named 'key'
    ball = Column(Integer)  # Additional integer column named 'ball'


engine = create_engine('sqlite:////mnt/myssd/urn.db', echo=True)  # echo=True will log all generated SQL
Base.metadata.create_all(engine)
