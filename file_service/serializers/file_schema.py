from file_service import ma

from marshmallow import fields


class FileSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    file_name = fields.Str(dump_only=True)
    file_size = fields.Integer()
    file_hash = fields.Str()
    file_path = fields.Str(dump_only=True)