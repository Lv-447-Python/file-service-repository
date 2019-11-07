from file_service import app

from file_service.views.index import FileLoading, api


api.add_resource(FileLoading, '/')