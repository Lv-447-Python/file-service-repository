from file_service import ma
from marshmallow import fields

from file_service.models.file import File


class FileSchema(ma.ModelSchema):
    class Meta:
        model = File

