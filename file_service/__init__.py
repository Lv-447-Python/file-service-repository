from flask import Flask
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app     = Flask(__name__)
api     = Api(app)
ma      = Marshmallow(app)
db      = SQLAlchemy(app)
migrate = Migrate(app, db)