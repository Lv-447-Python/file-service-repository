from file_service import app, db

from file_service.models.file import File

from sqlalchemy.orm import sessionmaker

from flask.views import MethodView

from flask import jsonify



class FileLoading(MethodView):
    #TODO Create doc string for class description

    def get(self):
        return '<h1>Test</h1>'

    def post(self):
        return jsonify({
            'Name': 'Benis',
            'Comment': 'Haha',
            'Is it working?': 'X----------D'
        })
    
    def __str__(self):
        return 'Class FileLoading - initilized'



# @app.route('/')
# def index():

#     db.create_all()
#     db.session.add(File('name', 'path', 'meta'))

#     result = File.query.all()

#     for row in result:
#         print(row.file_name + '\t|\t' + row.file_path + '\t|\t' + row.file_meta)

#     return '<h1>Test</h1>'
