"""
Module for initialization basic modules and instances for whole project
"""
import logging
from flask_marshmallow import Marshmallow
from flask_script import Manager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask import Flask


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(name)s | %(levelname)s: %(message)s')
# in common library !!!
POSTGRES = {
    'user': 'postgres',
    'pw': '',
    'db': 'statcrutch',
    'host': 'db',
    'port': '5432',
}

APP = Flask(__name__)

API = Api(APP)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['UPLOAD_FOLDER'] = 'files/'

DB = SQLAlchemy(APP)
MA = Marshmallow(APP)

MIGRATE = Migrate(APP, DB)
MANAGER = Manager(APP)
MANAGER.add_command('db', MigrateCommand)
from file_service.models.file import File
