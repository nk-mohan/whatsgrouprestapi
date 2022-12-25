from flask import Flask
from flask.json import jsonify
import os
from src.auth import auth
from src.whatsgroups import whatsgroups
from src.database import db
from flask_jwt_extended import JWTManager
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLASQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),

            SWAGGER={
                "title":"WhatsGroups API",
                "uiversion":3
            }
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    engine = create_engine(os.environ.get("SQLALCHEMY_DB_URI"))
    if not database_exists(engine.url):
      create_database(engine.url)
    engine.connect()

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(whatsgroups)

    Swagger(app, config=swagger_config, template=template)
    
    @app.errorhandler(HTTP_403_FORBIDDEN)
    def handle_403(e):
        return jsonify({"error": "It's a forbidden action"}), HTTP_403_FORBIDDEN

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({"error": "Something went wrong, we are working on it"}), HTTP_500_INTERNAL_SERVER_ERROR

    return app


