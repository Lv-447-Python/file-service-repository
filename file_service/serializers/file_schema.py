from file_service import ma
<<<<<<< HEAD

=======
>>>>>>> origin/draft_resources
from marshmallow import fields


class FileSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    file_name = fields.Str(dump_only=True)
    file_size = fields.Integer()
    file_hash = fields.Str()
<<<<<<< HEAD
    file_path = fields.Str(dump_only=True)
=======
    file_path = fields.Str(dump_only=True)
>>>>>>> origin/draft_resources
