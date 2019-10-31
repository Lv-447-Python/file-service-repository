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


POSTGRES = {
    'user': 'postgres',
    'pw': '02082001',
    'db': 'statcrutch',
    'host': 'localhost',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



from file_service.views import index




