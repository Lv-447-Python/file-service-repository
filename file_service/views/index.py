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



def extract_filters(file_path):
    filters = []
    
    try:
        with open(file_path) as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')
            
            filters = [filter.capitalize() for filter in list(csv_reader)[0]]
            
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

        sha256_hash = hashlib.sha256()              
        piece_size  = 65536                          
        byte_line   = file_content.read(piece_size)

        while len(byte_line) > 0:                   
            sha256_hash.update(byte_line)         
            byte_line = file_content.read(piece_size) 
        return sha256_hash.hexdigest()                 

    @staticmethod
    def check_for_unique(file_hash, file_size):

        possible_files = [file_instance for file_instance in
                          File.query.filter_by(file_size=file_size)] 

        if len(possible_files) == 0:  
            return True
        else:
            possible_files_hashes = [file_instance.file_hash for file_instance in possible_files]  
            if binary_search(sorted(possible_files_hashes), file_hash): 
                exist_file = [existed for existed in File.query.filter_by(file_hash=file_hash)]  
                return exist_file[0].file_path 
            else:
                return True  


    @staticmethod
    def generate_meta_and_filters(file_instance):

        file_size = len(file_instance.read())

        file_instance.stream.seek(0)
        
        file_hash = FileLoading.generate_hash(file_instance)

        file_instance.stream.seek(0)

        filename  = secure_filename(file_instance.filename)

        file_path = ''

        is_unique = FileLoading.check_for_unique(file_hash, file_size)
        if is_unique == True:
            file_path = app.config['UPLOAD_FOLDER'] + filename
            file_instance.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            file_path = is_unique

        print(file_path)
        filters = extract_filters(file_path)
        print(filters)

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
        
        if 'userfile' not in request.files:
            return redirect(request.url)
        file = request.files['userfile']

        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        meta = FileLoading.generate_meta_and_filters(file)

        input_file = File(*meta[0])

        file_schema = FileSchema()

        FileLoading.add_file_to_db(input_file) 


        filters = meta[1]
        data    = file_schema.dump(input_file)


        return jsonify({
            'data': data,
            'filters': filters,
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

        result = None 
        path   = ''   
        msg    = ''   

        requested_id = request.args.get('file_id', type=int)  

        if requested_id >= 1:                                              
            resulted_file = File.query.filter_by(id=requested_id).first()  


            if resulted_file is not None:                                  
                path = resulted_file.file_path                             
                msg  = 'Success'                                           

                result = jsonify({                                         
                    'path': path,
                    'msg': msg,
                    'status': status.HTTP_200_OK })                        
            else:
                msg = 'File with such id not found'                        

                result = jsonify({ 
                    'path': path,
                    'err': msg,
                    'status': status.HTTP_404_NOT_FOUND })
        else:
            msg = 'There is no files with such id'

            result = jsonify({
                'path': path,
                'err': msg,  
                'status': status.HTTP_404_NOT_FOUND})                     

        return result   


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
