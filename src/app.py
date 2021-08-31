from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from flask import request, jsonify
from flask_cors import CORS
from pprint import pprint
from urllib.parse import parse_qs
from os import environ
import ssl
import json
import subprocess

from tfstack_blueprint import tfstack_blueprint

def create_app(tf_dir):
    """creates the flask app with the needed blueprints including swaggerui

    Args:
        tf_dir (str): the path to the directory containing terraform execution shell scripts

    Returns:
        Flask app: configured flask app that can be started
    """
    app = Flask(__name__)
    CORS(app)

    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={'app_name': "tfstack-api"})
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    app.register_blueprint(tfstack_blueprint)

    app.config['TF_DIR'] = tf_dir

    return app


def main():
    """main function for the tfstack-api API component

      The tfstack-api exposes a simple (mostly) asynchronous API that is able to CRUD a particular Terraform configuration,
      instantiating Terraform 'stacks', basically abstracting the nuts and bolts of Terraform.

      Expected environment variables:
        TF_DIR: the path to the directory containing terraform execution shell scripts
    """
    tf_dir = environ['TF_DIR']

    app = create_app(tf_dir)

    app.run(host="0.0.0.0", port=8080)


if __name__ == '__main__':
    main()
