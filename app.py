from sqlalchemy import (create_engine, Column,
                        String, Integer, Date)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import csv
import datetime
import time


engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated =  Column(Date)


def organise_csv_data(inventory_file):
    with open(inventory_file) as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            print(row)
            

if __name__ == '__main__':
    # Base.metadata.create_all(engine)

    organise_csv_data('inventory.csv')
    