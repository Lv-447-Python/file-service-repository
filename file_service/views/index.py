from file_service import app, db

from file_service.models.file import File

from sqlalchemy.orm import sessionmaker

@app.route('/')
def index():
    
    '''
    id        = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), unique=False, nullable=False)
    file_meta = db.Column(db.Text, unique=False, nullable=False)
    file_path = db.Column(db.Text(200), unique=True, nullable=False)
    '''

    result = File.query.all()

    for row in result:
        print(row.file_name + '\t|\t' + row.file_path + '\t|\t' + row.file_meta)

    return '<h1>HAHA BENIS</h1>'