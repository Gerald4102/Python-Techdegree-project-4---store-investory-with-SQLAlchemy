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
        # next two lines before the for-loop are modified from: 
        # https://stackoverflow.com/questions/10079216/skip-first-entry-in-for-loop-in-python
        data = iter(csv.reader(csvfile))
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
    add_to_db(products)


def add_to_db(list_of_dictionaries):
    for item in list_of_dictionaries:
        product_in_db = session.query(Product) \
                        .filter(Product.product_name==item['product_name']) \
                        .one_or_none()
        if product_in_db == None:
            new_product = Product(product_name=item['product_name'], 
                                  product_price=item['product_price'],
                                  product_quantity=item['product_quantity'], 
                                  date_updated=item['date_updated'])
            session.add(new_product)
            print('Product added')
        elif product_in_db.date_updated < item['date_updated']:
            product_in_db.product_price = item['product_price']
            product_in_db.product_quantity = item['product_quantity']
            product_in_db.date_updated = item['date_updated']
            print('Product updated')
        else:
            print('No change. Product is already up to date in the database.')
    session.commit()


def clean_price(price_str):
    try:
        price = price_str.split('$')[1]
        price = float(price) * 100
        price = round(price, 0)
    except ValueError:
        print('Try again!')
        return
    return int(price)
    

def clean_quantity(quantity_str):
    try:
        quantity = int(quantity_str)
    except ValueError:
        print('Try again!')
        return
    else:
        return quantity


def clean_date(date_str):
    date = date_str.split('/')
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])
    return datetime.date(year, month, day)


def menu():
    menu_running = True
    while menu_running:
        print('''
        \n************ STORE INVENTORY *************
        \r
        \rView details of a product by ID (v)
        \rAdd new product to the database (a)
        \rBackup entire contents of the database (b)
        \rQuit (q)
        \r
        \r******************************************''')
        choice = input('Please choose v, a, b or q and press ENTER: ')
        if choice == 'v':
            view_product()
        elif choice == 'a':
            add_product()
        elif choice == 'b':
            backup_db()
        elif choice == 'q':
            menu_running = False
        else:
            input('Invalid option. Press Enter to continue...')


def view_product():
    choice_error = True
    while choice_error:
        prod_ids_tuples = session.query(Product.product_id).all()
        prod_ids = str([int(id[0]) for id in prod_ids_tuples])
        print(f'\nProduct IDs: {prod_ids[1:len(prod_ids)-1]}')
        prod_id = input('Please choose a product ID: ')
        if prod_id in prod_ids:
            choice_error = False
        else:
            print('That is not a valid ID')
            time.sleep(1.2)
    product = session.query(Product).filter(Product.product_id==int(prod_id)).one()
    print(f'''
          \rID: {product.product_id}
          \rProduct: {product.product_name}
          \rQuantity: {product.product_quantity}
          \rPrice: £{format(product.product_price/100, '.2f')}
          \rUpdated: {datetime.date.strftime(product.date_updated, '%x')}
          \r''')
    input('Press Enter to continue... ')


def add_product():
    name = input('\nEnter the Product Name: ')
    quantity_error = True
    while quantity_error:
        quantity = input('Enter the quantity (E.g. 42): ')
        quantity = clean_quantity(quantity)
        if type(quantity) == int:
            quantity_error = False
    price_error = True
    while price_error:
        price = input('Enter the price without a currency symbol (E.g. 15.99): ')
        price = clean_price('$'+price)
        if type(price) == int:
            price_error = False
    date = datetime.date.today()
    product = [{'product_name': name,
               'product_price': price,
               'product_quantity': quantity,
               'date_updated': date}]
    add_to_db(product)
    input('Press Enter to continue... ')


def backup_db():
    with open('inventory_new.csv', 'w') as csvfile:
        csvfile.write('product_name,product_price,product_quantity,date_updated')
        data = session.query(Product).all()
        for row in data:
            if ',' in row.product_name:
                name = '"{}"'.format(row.product_name)
            else:
                name = row.product_name
            price = format(row.product_price/100, '.2f')
            quantity = row.product_quantity
            # change '%#m/%#d/%Y' to '%-m/%-d/%Y' for UNIX-type platforms
            date = row.date_updated.strftime('%#m/%#d/%Y')
            csvfile.write(f'\n{name},${price},{quantity},{date}')
    input('Backup complete. Press Enter to continue...')


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    create_existing_products_list('inventory_new.csv')
    menu()