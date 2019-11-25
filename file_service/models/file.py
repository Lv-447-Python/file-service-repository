"""Model for file service."""
from file_service import DB


class File(DB.Model):
    """
    This module demonstrates database table file by class.
    """
    __tablename__ = 'file'

    id = DB.Column(DB.Integer, primary_key=True)
    file_name = DB.Column(DB.String(100), unique=False, nullable=False)
    file_size = DB.Column(DB.Integer, unique=False, nullable=False)
    file_hash = DB.Column(DB.Text, unique=False, nullable=False)
    file_path = DB.Column(DB.Text, unique=False, nullable=False)

    def __init__(self, file_name, file_size, file_hash, file_path):
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        self.file_path = file_path

    def __repr__(self):
        return f'\t File: {self.file_name}'
