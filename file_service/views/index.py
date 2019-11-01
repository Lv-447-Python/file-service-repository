import os
from werkzeug.utils import secure_filename, redirect
from flask.views import MethodView
from flask import jsonify, request, render_template

ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileLoading(MethodView):
    # TODO Create doc string for class description

    def get(self):
        return render_template('index.html')

    def post(self):
        # check if the post request has the file part
        if 'filename' not in request.files:
            return redirect(request.url)
        file = request.files['filename']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        file.save(os.path.join('.', file.filename))
        return f'Uploaded {file.filename}'

    def __str__(self):
        return 'Class FileLoading - initilized'
