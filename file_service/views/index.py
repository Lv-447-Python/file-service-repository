import os

from flask_api import status
from flask_restful import Resource

from file_service import app, db, api
from file_service.models.file import File
from file_service.serializers.file_schema import FileSchema

from werkzeug.utils import secure_filename, redirect
from flask import jsonify, request, render_template, session, make_response

from sqlalchemy import exc

import requests
import hashlib
import datetime
import csv
from requests.exceptions import HTTPError
from file_service import logging

FILE_SCHEMA = FileSchema()
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}


def binary_search(file_hashes, hash_value):
    if type(file_hashes) not in (tuple, list) or type(hash_value) != str:
        raise TypeError('Type Error: file_hashes should be iterable object (list/tuple)\n\
                                     hash_value should be string')

    if len(file_hashes) < 1:
        return False

    index = int(len(file_hashes) / 2)

    possible_element_hash = file_hashes[index]

    if hash_value == possible_element_hash:
        return True
    elif hash_value > possible_element_hash and len(file_hashes) >= 1:
        return binary_search(file_hashes[index + 1:], hash_value)
    elif hash_value < possible_element_hash and len(file_hashes) >= 1:
        return binary_search(file_hashes[0: index - 1], hash_value)
    else:
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_filters(file_path):
    filters = []

    try:
        with open(file_path) as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')

            filters = [filter.capitalize() for filter in list(csv_reader)[0]]

            logging.info(f'From ||{file_path}|| extracted filters: {filters}\n')

    except FileNotFoundError:
        logging.error(f'Error with opening file by path: || {file_path} ||, not found')

    return filters


class FileLoading(Resource):

    @staticmethod
    def generate_hash(file_content):
        sha256_hash = hashlib.sha256()
        piece_size  = 65536
        byte_line   = ''

        try:
            byte_line = file_content.read(piece_size)
            logging.info('File read correctly')
        except TypeError:
            logging.error('Type Error: can read only string(byte-like) objects')

        while len(byte_line) > 0:
            sha256_hash.update(byte_line)
            byte_line = file_content.read(piece_size)

        file_content.stream.seek(0)

        return sha256_hash.hexdigest()

    @staticmethod
    def check_for_unique(file_hash, file_size):

        possible_files = [file_instance for file_instance in
                          File.query.filter_by(file_size=file_size)]

        if len(possible_files) == 0:
            logging.info('File is unique')
            return True
        else:
            possible_files_hashes = [file.file_hash for file in possible_files]
            if binary_search(sorted(possible_files_hashes), file_hash):
                exist_file = [existed for existed in File.query.filter_by(file_hash=file_hash)]

                logging.info(f'File already in DB, so set with path: {exist_file[0].file_path}')

                return exist_file[0].file_path
            else:
                logging.info('File is unique')
                return True

    @staticmethod
    def generate_meta_and_filters(file_instance):

        file_size = len(file_instance.read())

        file_instance.stream.seek(0)

        file_hash = FileLoading.generate_hash(file_instance)
        filename = secure_filename(file_instance.filename)

        is_unique = FileLoading.check_for_unique(file_hash, file_size)

        if is_unique:
            file_path = app.config['UPLOAD_FOLDER'] + filename
            file_instance.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            file_path = is_unique

        filters = extract_filters(file_path)

        return [filename, file_size, file_hash, file_path], filters

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

        return make_response(
            jsonify({
                'all_files': result
            }),
            status.HTTP_200_OK)

    def post(self):

        if 'user_file' not in request.files:
            return redirect(request.url)
        file = request.files['user_file']

        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        meta        = FileLoading.generate_meta_and_filters(file)

        input_file  = File(*meta[0])

        file_schema = FileSchema()

        FileLoading.add_file_to_db(input_file)

        filters = meta[1]
        data    = file_schema.dump(input_file)

        return make_response(
            jsonify({
                'data': data,
                'filters': filters
            }),
            status.HTTP_201_CREATED)

    def __str__(self):
        return 'Class FileLoading - initilized'


def decorate_specific_operation(operation):
    def file_finding_handler(resource_method):
        def wrapper(*args, **kwargs):

            file = resource_method(args, kwargs['file_id'])

            if file is not None:
                if operation == 'GET':
                    result = make_response(
                        jsonify({
                            'path': file.file_path,
                            'message': 'Success'
                        }),
                        status.HTTP_200_OK
                    )

                if operation == 'DELETE':
                    FileInterface.delete_file_from_db(file)

                    result = make_response(
                        jsonify({
                            'msg': 'File successfully deleted'
                        }),
                        status.HTTP_200_OK
                    )
            else:
                result = make_response(
                    jsonify({
                        'msg': 'File with such id not found'
                    }),
                    status.HTTP_404_NOT_FOUND)

            return result

        return wrapper
    return file_finding_handler


class FileInterface(FileLoading):

    @staticmethod
    def delete_file_from_db(file):
        if not isinstance(file, File):
            raise TypeError('file should be instance of File model class')

        db.session.delete(file)
        db.session.commit()

    @decorate_specific_operation('GET')
    def get(self, file_id):

        requested_file = File.query.filter_by(id=file_id).first()

        return requested_file

    @decorate_specific_operation('DELETE')
    def delete(self, file_id):

        requested_file_to_delete = File.query.filter_by(id=file_id).first()

        return requested_file_to_delete
