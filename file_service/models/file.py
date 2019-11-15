"""Model for file service."""
from file_service import db


class File(db.Model):
    """
    This module demonstrates database table file by class.
    """
    __tablename__ = 'file'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), unique=False, nullable=False)
    file_size = db.Column(db.Integer, unique=False, nullable=False)
    file_hash = db.Column(db.Text, unique=False, nullable=False)
    file_path = db.Column(db.Text, unique=False, nullable=False)

    def __repr__(self):
        return f'\t File: {self.file_name}'


