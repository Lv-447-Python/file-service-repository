import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from file_service import app, db

app.config.from_object(os.environ['APP_SETTINGS'])
POSTGRES = {
    'user': 'postgres',
    'pw': '02082001',
    'db': 'statcrutch',
    'host': 'localhost',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()