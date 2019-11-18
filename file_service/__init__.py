from flask import Flask
from flask_marshmallow import Marshmallow
from flask_script import Manager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

POSTGRES = {
    'user': 'postgres',
    'pw': '02082001',
    'db': 'statcrutch',
    'host': '127.0.0.1',
    'port': '5432',
}

app = Flask(__name__, template_folder='templates')
api = Api(app)

app.debug = True

api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'files/'

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from file_service.views import routes