from file_service import app

from file_service.views.index import FileLoading

file_view = FileLoading.as_view('file_view')

app.add_url_rule('/', view_func=file_view, methods=['GET', 'POST'])