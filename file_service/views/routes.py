from file_service import api, app

from file_service.views.index import FileLoading, FileInterface
from file_service.views.file_filtering import FileFiltering
from file_service.views.myviewer import MyViewer

api.add_resource(FileLoading, '/')
api.add_resource(FileInterface, '/file')
api.add_resource(FileFiltering, '/filtering')
