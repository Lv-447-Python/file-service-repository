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
    def hash_file(file_obj):

        sha256_hash = hashlib.sha256()

        try:
            with open(file_obj, 'r+b') as f:
                # Read and update hash string value in blocks of 4K
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
                
                

                # move file cursor to end
                f.seek(0, os.SEEK_END)

                
                return {
                    'hash': sha256_hash.hexdigest(),
                    'size': f.tell()
                }

        except Exception:
            print('Some pronlem with file')
        '''Creates file hash for future manipulating'''

        
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

        loaded_file = FileLoading.hash_file(file.filename)

        print('*' * 50)
        print('\tUploaded {0}\
        \n\t File hash:{1}\
        \n\t Loaded: {2}\
        \n\t Size: {3}'.format(file.filename, loaded_file['hash'], datetime.datetime.now(), loaded_file['size']))
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))



        return 'haha'

    def __str__(self):
        return 'Class FileLoading - initilized'
