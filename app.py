from flask import Flask
import requests
from requests import HTTPError

app = Flask(__name__)

@app.route('/')
def base():
    return "Hello you seem to be lost. Please check /products/{id} for more meaningful product information"


@app.route('/products/<id>', methods=['GET'])
def get_product_by_id(id):

    # Builds URL for Redsky to get actual data
    url = "https://redsky.target.com/v2/pdp/tcin/{}?excludes=taxonomy,price,promotion,bulk_ship,rating_and_review_reviews,rating_and_review_statistics,question_answer_statistics".format(id)


    # Returns JSON object of product with given ID
    response = requests.get(url)

    try:
        response.raise_for_status()

    except HTTPError as http_err:
        return 'An error has occurred:' + http_err

    except Exception as err:
        return 'An error has occurred:' + err


    print(response.text)
    return id

@app.route('/products/<int:id>', methods=['PUT', 'POST'])
def set_product_by_id(id):
    # Updates product info and returns newly updated info
    return id




app.run()