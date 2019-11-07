import os

from flask import jsonify, request, render_template, session
from flask_restful import Resource
from werkzeug.utils import secure_filename, redirect
from flask.views import MethodView
from file_service import app, db, api
from file_service.models.file import File

from file_service.serializers.file_schema import FileSchema

import hashlib
import datetime

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}


def binary_search(file_hashes, hash_value):

    if type(file_hashes) not in (tuple, list) or type(hash_value) != str:
        raise TypeError('Type Error: file_hashes should be iterable object (list/tuple)\n\
                                     hash_value should be string')
    

    index = int(len(file_hashes) / 2)

    possible_element_hash = file_hashes[index]
    
    
    if hash_value == possible_element_hash:
        return True
    elif hash_value > possible_element_hash:
        if index == len(file_hashes) - 1:
            return False
        return binary_search(file_hashes[index + 1:], hash_value)
    else:
        return binary_search(file_hashes[0: index], hash_value)
    
    return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileLoading(Resource): 

    @staticmethod
    def generate_hash(file_content):

        print(file_content)
        try:
            file_content = str(file_content)
        except TypeError as e:
            print('File Content should be byte array string, \n', e)
            return

        sha256_hash = hashlib.sha256()                # create instance of sha256 algorithm from hashlib

        piece_size  = 4096                            # amount of bits which will be read for 1 iteration

        byte_line   = file_content.read(piece_size)   # read file content as bytes

        while len(byte_line) > 0:                     # means it's not the end of the file
            sha256_hash.update(byte_line)             # update hash for every piece_size

            byte_line = file_content.read(piece_size) # update value
        
        return sha256_hash.hexdigest()                # return hash value
    
    @staticmethod
    def check_for_unique(file_hash, file_size):

        possible_files = [file for file in File.query.filter_by(file_size=file_size)]            # get all files with such file_size

        if len(possible_files) == 0:                                                             # means this file is unique
            return True
        else:
            possible_files_hashes = [file.file_hash for file in possible_files]                  # get hashes of all possible files

            if binary_search(sorted(possible_files_hashes), file_hash):                          # if we found file with such hash
                exist_file = [existed for existed in File.query.filter_by(file_hash=file_hash)]  # get the existed file
                print('//////////////////////////////////', exist_file[0])
                return exist_file[0].file_path                                                   # get it's physical file path

            else:
                return True                                                                      # file is unique


        print(possible_files_hashes)

        
        
    # TODO Create doc string for class description

    def get(self):

        return jsonify({'haha': 'benis'})

    def post(self):

        # check if the post request has the file part

        

        if 'filename' not in request.files:
            return redirect(request.url)
        file = request.files['filename']

        

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        print(file.read())

        file.stream.seek(0)

        file_size = len(file.read())    

        file.stream.seek(0)

        file_hash = FileLoading.generate_hash(file)


        file.stream.seek(0) # move pointer to the start of the file

        filename = secure_filename(file.filename)
        
        file_path = ''

        is_unique = FileLoading.check_for_unique(file_hash, file_size)
        
        if is_unique == True:
            file_path = app.config['UPLOAD_FOLDER'] + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            file_path = is_unique


        input_file = File(filename, file_size, file_hash, file_path)

        db.session.add(input_file)
        db.session.commit()

        
        return 'Success'

    def __str__(self):
        return 'Class FileLoading - initilized'

