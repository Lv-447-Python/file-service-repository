from file_service import app, db

from file_service.models.file import File

from sqlalchemy.orm import sessionmaker


@app.route('/')
def index():

    db.create_all()
    db.session.add(File('name', 'path', 'meta'))

    result = File.query.all()

    for row in result:
        print(row.file_name + '\t|\t' + row.file_path + '\t|\t' + row.file_meta)

    return '<h1>HAHA BENIS X---------DDDDDDDDDDD</h1>'
