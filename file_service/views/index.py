"""Initial point in file service"""
import os
import hashlib
import csv

from functools import wraps

from flask import jsonify, request, make_response
from flask_api import status
from flask_restful import Resource

from werkzeug.utils import secure_filename, redirect

from file_service import APP, DB, API, File
from file_service.serializers.file_schema import FileSchema
from file_service import logging


ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}


def binary_search(file_hashes, hash_value):
    """
    Binary search algorithm in order to identify if file with such content already in DB
    Args:
        file_hashes (list):
        hash_value (str)
    Returns:
        True if hash found, False otherwise
    """
    if not (isinstance(file_hashes, (list, tuple)) or not isinstance(hash_value, str)):
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
    """Function for checking file extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_headers(file_path):
    """
    Function for extracting headers from file by it's path
    Args:
        file_path (str):
    Returns:
        list of headers
    """
    headers = []

    try:
        with open(file_path) as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')

            headers = [header.capitalize() for header in list(csv_reader)[0]]

            logging.info(f'From ||{file_path}|| extracted headers: {headers}\n')

    except FileNotFoundError:
        logging.error(f'Error with opening file by path: || {file_path} ||, not found')

    return headers


class FileLoading(Resource):
    """
    Resource for working with files
    methods:
        GET:  localhost:/files ==> return all files meta-data
        POST: localhost:/files ==> (with request file) load file to DB and show user meta-data and headers
    """

    @staticmethod
    def generate_hash(file_content):
        """
        Function for generating hash value based on file content
        Args:
            file_content (buffer)
        Returns:
            hash string
        """
        sha256_hash = hashlib.sha256()
        piece_size = 65536
        byte_line = ''

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
        """
        Function to identify if file is unique
        Args:
            file_hash (str):
            file_size (int):
        Returns:
            True if file unique, str file path otherwise
        """

        possible_files = [file_instance for file_instance in
                          File.query.filter_by(file_size=file_size)]

        if len(possible_files) == 0:
            logging.info('File is unique')
            result = True
        else:
            possible_files_hashes = [file.file_hash for file in possible_files]
            if binary_search(sorted(possible_files_hashes), file_hash):
                exist_file = [existed for existed in File.query.filter_by(file_hash=file_hash)]

                logging.info(f'File already in DB, so set with path: {exist_file[0].file_path}')

                result = exist_file[0].file_path
            else:
                logging.info('File is unique')
                result = True

        return result

    @staticmethod
    def generate_meta_and_headers(file_instance):
        """
        Function for generating meta-data and headers of loaded dataset
        Args:
            file_instance (buffer)
        Returns:
            tuple of lists
                1) list of file metadata
                2) list of headers of dataset
        """

        file_size = len(file_instance.read())

        file_instance.stream.seek(0)

        file_hash = FileLoading.generate_hash(file_instance)
        filename = secure_filename(file_instance.filename)

        is_unique = FileLoading.check_for_unique(file_hash, file_size)

        if is_unique:
            file_path = APP.config['UPLOAD_FOLDER'] + filename
            file_instance.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
        else:
            file_path = is_unique

        headers = extract_headers(file_path)

        return [filename, file_size, file_hash, file_path], headers

    @staticmethod
    def add_file_to_db(file):
        """
        Function for adding file to database
        Args:
            file (File):
        """
        if not isinstance(file, File):
            raise TypeError('file should be a File instance.')

        DB.session.add(file)
        DB.session.commit()

    def get(self):
        """GET method for getting list of all files in DB"""

        file_schema = FileSchema(many=True)

        print('before query')
        all_files = File.query.all()

        result = file_schema.dump(all_files)

        return make_response(
            jsonify({
                'all_files': result
            }),
            status.HTTP_200_OK)

    def post(self):
        """POST method for loading user's file into DB"""

        if 'user_file' not in request.files:
            return redirect(request.url)
        file = request.files['user_file']

        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        meta = FileLoading.generate_meta_and_headers(file)

        input_file = File(*meta[0])

        file_schema = FileSchema()

        FileLoading.add_file_to_db(input_file)

        filters = meta[1]
        data = file_schema.dump(input_file)

        return make_response(
            jsonify({
                'data': data,
                'filters': filters
            }),
            status.HTTP_201_CREATED)


def file_finding_handler(resource_method):
    """Decorator function for resource methods"""
    @wraps(resource_method)
    def wrapper(*args, **kwargs):
        response = resource_method(args, kwargs['file_id'])

        not_found_response = make_response(
            jsonify({
                'error': 'File with such id not found'
            }),
            status.HTTP_404_NOT_FOUND
        )

        return response if response is not None else not_found_response

    return wrapper


class FileInterface(FileLoading):
    """
    Resource for working with single file
    methods:
        GET:  localhost:/file/<file_id:int> ==> return file path by requested file_id
        PUT:  localhost:/file/<file_id:int> ==> filter data frame by requested form values
        POST: localhost:/file/<file_id:int> ==> save filtered data frame and requested form values
    """

    @staticmethod
    def delete_file_from_db(file):
        """
        Function for deleting file from database
        Args:
            file (File):
        """
        if not isinstance(file, File):
            logging.error('file is not instance of File model')
            raise TypeError

        DB.session.delete(file)
        DB.session.commit()

    @file_finding_handler
    def get(self, file_id):
        """GET method for getting file path by specific file_id"""
        requested_file = File.query.filter_by(id=file_id).first()

        try:
            result = make_response(
                jsonify({
                    'path': requested_file.file_path,
                    'message': 'Success'
                }),
                status.HTTP_200_OK
            )
            return result

        except AttributeError:
            logging.error(f'File with id: {file_id}, not found')
            return None

    @file_finding_handler
    def delete(self, file_id):
        """DELETE method for deleting file from db by specific file_id"""
        requested_file_to_delete = File.query.filter_by(id=file_id).first()

        try:
            FileInterface.delete_file_from_db(requested_file_to_delete)

            result = make_response(
                jsonify({
                    'message': 'Success, file deleted'
                }),
                status.HTTP_200_OK)

            return result
        except TypeError:
            return None


API.add_resource(FileLoading, '/files')
API.add_resource(FileInterface, '/file/<int:file_id>')
