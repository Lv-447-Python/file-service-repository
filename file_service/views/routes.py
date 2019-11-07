from file_service import app

from file_service.views.index import FileLoading, api

file_view = FileLoading.as_view('file_view')

api.add_resource(FileLoading, '/')