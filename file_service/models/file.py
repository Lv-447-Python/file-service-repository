from file_service import db


class File(db.Model):
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), unique=False, nullable=False)
    file_meta = db.Column(db.Text, unique=False, nullable=False)
    file_path = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'\t File: {self.file_name}'
