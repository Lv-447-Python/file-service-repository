"""Module for describing of model schema"""
from file_service import MA
from file_service.models.file import File


class FileSchema(MA.ModelSchema):
    """Model schema class"""
    class Meta:
        """Meta class where we define actually model class in order to work with"""
        model = File
