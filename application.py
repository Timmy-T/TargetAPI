import requests
from flask import Flask, json, request
from tinydb import TinyDB, Query

from models import *

app = Flask(__name__)
db = TinyDB('db.json')


def initialize_db():
    """
    Initializes the database with a single row and price data point for Big Lebowski
    :return: None
    """

    app.logger.info("Purging Database")
    db.purge()

    app.logger.info("Populating Database")
    sample_product = {'id': 13860428, 'price': '13.49', 'currency': 'USD'}
    db.insert(sample_product)


@app.route('/')
def base():
    return "Hello you seem to be lost. Please check /products/{id} for more meaningful product information", 404


@app.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    """
    Gets Product information from RedSky API and NoSQL DB
    :param id: Product ID - Unique Key
    :return: 200 - Product Model
             4XX, 5XX - Error Msg and matching response code
    """

    # Builds URL for RedSky endpoint
    url = ("https://redsky.target.com/v2/pdp/tcin/{0}"
           "?excludes=taxonomy,price,promotion,bulk_ship,rating_and_review_reviews,"
           "rating_and_review_statistics,question_answer_statistics").format(id)

    response = requests.get(url)

    try:
        response.raise_for_status()

    except requests.HTTPError:
        if response.status_code == 404:
            return json.jsonify('Product ID:{0} not found'.format(id)), 404

        # If non-404 error propagate
        app.logger.error("An error has occurred:" + str(response.status_code))
        return json.jsonify('An error has occurred'.format(id)), response.status_code

    except Exception as err:
        app.logger.error("An error has occurred:" + str(err))
        return json.jsonify('An error has occurred'), 500

    product_data = response.json()
    name = product_data['product']['item']['product_description']['title']

    product = Product(id=id, name=name, price_data=__get_price_data(id))

    return json.jsonify(ProductSchema().dump(product).data)


def __get_price_data(id):
    """
    Fetches Price Data object from data store
    :param id: Product ID
    :return: PriceData model if found or None
    """
    price_query = Query()
    result = db.get(price_query.id == id)
    if result is not None:
        return PriceData(result["price"], result["currency"])
    return None


@app.route('/products/<int:id>', methods=['PUT', 'POST'])
def set_product_price_by_id(id):
    """
    Updates Product Price data in NoSQL data store
    :param id: ID to update - Unique Key
    :return: 200 - Product data with updated price
             404 - Product not found
             4XX, 5XX - Error response and matching code
    """
    # Updates product info and returns newly updated info
    data = request.get_json()
    price_data = data['current_price']

    if price_data is not None and price_data is not []:
        try:
            value = '%.2f' % float(price_data['value'])
            Price = Query()
            db.upsert({'id': id, 'price': value, 'currency': price_data['currency_code']}, Price.id == id)
            return get_product_by_id(id)

        except ValueError:
            pass  # We pass because we are checking if price is valid
        return "Invalid Currency Value", 400


if __name__ == "__main__":
    initialize_db()
    app.run()
