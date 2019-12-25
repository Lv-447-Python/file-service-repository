"""Initial Point of starting File Service (NOT FOR PRODUCTION DEPLOYMENT)"""

from file_service import APP

from file_service.views.index import FileLoading, FileInterface
from file_service.views.file_filtering import FileFiltering

if __name__ == "__main__":
    APP.run(host='0.0.0.0')
