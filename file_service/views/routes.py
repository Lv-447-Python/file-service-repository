from file_service import app, api

from file_service.views.index import FileLoading, FileInterface
from file_service.views.file_filtering import FileFiltering

api.add_resource(FileLoading, '/')
api.add_resource(FileInterface, '/file')
api.add_resource(FileFiltering, '/filtering')

# endpoint: /23 , /23/23/11


# orest хоче брати від мене файл path, він бере цей файл потім бере відфільтровані рядочки від валентина , і генерує з того файл 

# нам треба ендпоінт де ми будемо працювати з файлом тобто фільтрувати його, користувач працює з файлом, потім буде кнопка зберегти - і після цього запит летить в історію