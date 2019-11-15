from file_service import db


class File(db.Model):
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), unique=False, nullable=False)
    file_size = db.Column(db.Integer, unique=False, nullable=False)
    file_hash = db.Column(db.Text, unique=False, nullable=False)
    file_path = db.Column(db.Text, unique=False, nullable=False)

    def __init__(self, file_name, file_size, file_hash, file_path):
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.file_path = file_path

    def __repr__(self):
        return f'\t File: {self.file_name}'


