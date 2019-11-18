import os

from flask_api import status
from flask_restful import Resource

from file_service import app, db, api
from file_service.models.file import File
from file_service.serializers.file_schema import FileSchema

from werkzeug.utils import secure_filename, redirect
from flask import jsonify, request, render_template, session


from sqlalchemy import exc

import requests 
import hashlib
import datetime
import csv

from requests.exceptions import HTTPError

FILE_SCHEMA = FileSchema()
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



def extract_filters(file):
    filters = []
    
    try:
        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            
            for row in csv_reader:
                for single_filter in row:
                    filters.append(single_filter)
                break
    except Exception:
        print('Error with file')

    return filters


class FileLoading(Resource):
    

    @staticmethod
    def generate_hash(file_content):
        try:
            check = str(file_content)
        except TypeError as e:
            print('File Content should be byte array string, \n', e)
            return

        sha256_hash = hashlib.sha256()               # create instance of sha256 algorithm from hashlib
        piece_size  = 65536                          # amount of bits which will be read for 1 iteration
        byte_line   = file_content.read(piece_size)  # read file content as bytes

        while len(byte_line) > 0:                    # means it's not the end of the file
            sha256_hash.update(byte_line)            # update hash for every piece_size
            byte_line = file_content.read(piece_size)  # update value
        return sha256_hash.hexdigest()                 # return hash value

    @staticmethod
    def check_for_unique(file_hash, file_size):

        possible_files = [file_instance for file_instance in
                          File.query.filter_by(file_size=file_size)]  # get all files with such file_size

        if len(possible_files) == 0:  # means this file is unique
            return True
        else:
            possible_files_hashes = [file_instance.file_hash for file_instance in possible_files]  # get hashes of all possible files
            if binary_search(sorted(possible_files_hashes), file_hash):  # if we found file with such hash
                exist_file = [existed for existed in File.query.filter_by(file_hash=file_hash)]  # get the existed file
                return exist_file[0].file_path  # get it's physical file path
            else:
                return True  # file is unique

        #TODO Create logger config

    @staticmethod
    def generate_meta_and_filters(file_instance):

        current_file = file_instance.read()

        file_size = len(current_file)
        
        file_hash = FileLoading.generate_hash(current_file)

        filename  = secure_filename(file_instance.filename)

        file_path = ''

        is_unique = FileLoading.check_for_unique(file_hash, file_size)
        if is_unique == True:
            file_path = app.config['UPLOAD_FOLDER'] + filename
            file_instance.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            file_path = is_unique

        filters = extract_filters(file_path)

        return ([filename, file_size, file_hash, file_path], filters)

    @staticmethod
    def add_file_to_db(file):
        if not isinstance(file, File):
            raise TypeError('In order to add file to db, input value should be instance of File model.')
        
        db.session.add(file)
        db.session.commit()

    def get(self):
        file_schema = FileSchema(many=True)

        all_files = File.query.all()

        result = file_schema.dump(all_files) 

        return jsonify({
            'all_files': result,
            'status': status.HTTP_200_OK
        })
 

    def post(self):
        # check if the post request has the file part
        if 'userfile' not in request.files:
            return redirect(request.url)
        file = request.files['userfile']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        meta = FileLoading.generate_meta_and_filters(file)

        input_file = File(*meta[0])

        file_schema = FileSchema()

        FileLoading.add_file_to_db(input_file) # add and commit file to DB


        filters = meta[1]
        data    = file_schema.dump(input_file)


        try:
            file_filtering_url = 'http://127.0.0.1:5000/filtering'

            request_data = {'file_id': data['id'], 'filters': filters}

            file_filtering_response = requests.get(file_filtering_url, request_data)
        except HTTPError as err:
            print('*'*50, 'ERRRORR:', err)



        if True:
            return jsonify({
                'data': data,
                'filters': filters,
                'file_filtering_response': file_filtering_response.text,
                'status': status.HTTP_201_CREATED   
            })
        

    def __str__(self):
        return 'Class FileLoading - initilized'


class FileInterface(FileLoading):

    @staticmethod
    def delete_file_from_db(file):
        if not isinstance(file, File):
            raise TypeError('file should be instance of File model class')
        
        db.session.delete(file)
        db.session.commit()


    def get(self):

        result = None #
        path   = ''   # Response base values to return
        msg    = ''   #

        requested_id = request.args.get('file_id', type=int)               # get id from request arguments

        if requested_id >= 1:                                              # id should be positive ofc
            resulted_file = File.query.filter_by(id=requested_id).first()  # get file from DB with requested id


            if resulted_file is not None:                                  # if file found
                path = resulted_file.file_path                             # get path of founded file
                msg  = 'Succes'                                            # custom msg

                result = jsonify({                                         # result with arguments and status code 
                    'path': path,
                    'msg': msg,
                    'status': status.HTTP_200_OK })                        #----------------------------------------
            else:
                msg = 'File with such id not found'                        # otherwise msg

                result = jsonify({                                         # result when file is not found
                    'path': path,
                    'err': msg,
                    'status': status.HTTP_404_NOT_FOUND })
        else:
            msg = 'There is no files with such id'

            result = jsonify({
                'path': path,
                'err': msg,  
                'status': status.HTTP_404_NOT_FOUND})                      #----------------------------------------

        return result   # RESPONSE


    def delete(self):

        result = None
        msg    = ''

        file_to_delete_id     = request.args.get('file_id', type=int)

        file_to_delete_object = File.query.filter_by(id=file_to_delete_id).first()

        if file_to_delete_object is not None:
            msg = 'file successfuly deleted'

            FileInterface.delete_file_from_db(file_to_delete_object)

            result = jsonify({
                'msg': msg,
                'status': status.HTTP_200_OK
            })
        
        else:
            msg = 'file with such id not found'

            result = jsonify({
                'msg': msg,
                'status': status.HTTP_404_NOT_FOUND
            })

        return result
