import os

from file_service import app

from werkzeug.utils import secure_filename, redirect
from flask.views import MethodView
from flask import jsonify, request, render_template

import hashlib
import datetime

ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileLoading(MethodView): 

    @staticmethod
    def hash_file(file_content):

        sha256_hash = hashlib.sha256()

        piece_size  = 65536

        byte_line   = file_content.read(piece_size) # read file content as bytes

        while len(byte_line) > 0: # means it's not the end of the file
            sha256_hash.update(byte_line)

            byte_line = file_content.read(piece_size)
        
        return sha256_hash.hexdigest()
        
        
        
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

        file_size = len(file.read())
        

        loaded_file = FileLoading.hash_file(file)

        print('*' * 50)
        print('\tUploaded {0}\n\t File hash:{1}\n\t Loaded: {2}\n\t Size: {3}'.format(file.filename, loaded_file, datetime.datetime.now(), file_size))
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))



        return 'haha'

    def __str__(self):
        return 'Class FileLoading - initilized'