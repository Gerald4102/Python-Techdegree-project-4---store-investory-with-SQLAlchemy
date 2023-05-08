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


def create_existing_products_list(inventory_file):
    products = []
    with open(inventory_file) as csvfile:
        data = iter(csv.reader(csvfile))    # modified from: https://stackoverflow.com/questions/10079216/skip-first-entry-in-for-loop-in-python
        next(data)
        for row in data:
            product_name = row[0]
            product_price = clean_price(row[1])
            product_quantity = clean_quantity(row[2])
            date_updated = clean_date(row[3])
            product = {'product_name': product_name,
                       'product_price': product_price,
                       'product_quantity': product_quantity,
                       'date_updated': date_updated}
            products.append(product)
    add_csv_into_db(products)

def add_csv_into_db(list_of_dictionaries):
    for item in list_of_dictionaries:
        product_in_db = session.query(Product).filter(Product.product_name==item['product_name']).one_or_none()
        if product_in_db == None:
            new_product = Product(product_name=item['product_name'], product_price=item['product_price'],
                                product_quantity=item['product_quantity'], date_updated=item['date_updated'])
            session.add(new_product)
        elif product_in_db.date_updated < item['date_updated']:
            product_in_db.product_price = item['product_price']
            product_in_db.product_quantity = item['product_quantity']
            product_in_db.date_updated = item['date_updated']
    session.commit()


def clean_price(price_str):
    price = price_str.split('$')[1]
    price = float(price) * 100
    price = round(price, 0)
    return int(price)
    

def clean_quantity(quantity_str):
    return int(quantity_str)


def clean_date(date_str):
    date = date_str.split('/')
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])
    return datetime.date(year, month, day)


def menu():
    menu_running = True:
    while menu_running:
        print('''
        \n************ STORE INVENTORY *************
        \r
        \rView details of a product by ID (v)
        \rAdd new product to the database (a)
        \rBackup entire contents of the database (b)
        \rExit (e)
        \r
        \r******************************************''')
        choice = input('Please choose v, a, b or e and press ENTER: ')


if __name__ == '__main__':
    # Base.metadata.create_all(engine)

    # create_existing_products_list('inventory.csv')
  
    menu()