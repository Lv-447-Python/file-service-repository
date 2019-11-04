import os
from werkzeug.utils import secure_filename, redirect
from flask.views import MethodView
from flask import jsonify, request, render_template

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileLoading(MethodView):
    # TODO Create doc string for class description

    def get(self):
        return render_template('index.html')

    def post(self):
        if 'filename' not in request.files:
            return redirect(request.url)
        file = request.files['filename']
        if file.filename == '' or not allowed_file(file.filename):
            return f'Fuck you.'
        filename = secure_filename(file.filename)
        file.save(os.path.join('/home/alex/test', filename))
        return f'Uploaded file {file.filename}'

    def __str__(self):
        return 'Class FileLoading - initilized'
