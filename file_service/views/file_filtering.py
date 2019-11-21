import os

from flask_api import status
from flask_restful import Resource

from file_service import app, db, api
from file_service.models.file import File
from file_service.serializers.file_schema import FileSchema

from werkzeug.utils import secure_filename, redirect
from flask import jsonify, request, session, make_response


import requests
import hashlib
import datetime
import csv
import json
import pandas as pd


from requests.exceptions import HTTPError
from file_service import logging

from file_service.views.index import extract_filters


class FileFiltering(Resource):
    
    @staticmethod
    def filter_dataset(file_path, filters_dict):
        try:
            df = pd.read_csv(file_path, dtype=str)

            df.columns = [cols.capitalize() for cols in df]

            current_query = ''

            for key in filters_dict:
                if filters_dict[key] != '':
                    current_query += """ and """ if current_query != '' else ''
                    current_query += """{0} == '{1}'""".format(str(key), str(filters_dict[key]))

            logging.info(f'Will be filtered by query: \n{current_query}\n')

            filtered   = df.query(current_query) if current_query != '' else df

            result     = filtered.to_json(orient='index')

            return result
        except ValueError:
            logging.error(f'Error to read file as csv by path: {file_path}')
    

    def get(self, file_id):

        file_response = requests.get(f'http://127.0.0.1:5000/file/{file_id}')

        if file_response.status_code == 200:
            current_file_path    = file_response.json()['path']
            current_file_filters = extract_filters(current_file_path)

            response = make_response(
                jsonify({
                    'file_id': file_id,
                    'file_path': current_file_path,
                    'filters': current_file_filters,
                }),
                status.HTTP_200_OK
            )

        else:
            response = make_response(
                jsonify({'error': 'File not found'}),
                status.HTTP_404_NOT_FOUND
            )

        return response

    def put(self, file_id):
        requested_data = request.form

        current_file_response = requests.get(f'http://127.0.0.1:5000/file/{file_id}')

        if current_file_response.status_code == 200:
            current_file_path = current_file_response.json()['path']

            filters = extract_filters(current_file_path)

            result  = json.loads(FileFiltering.filter_dataset(current_file_path, requested_data))

            response = make_response(
                jsonify({
                    'filtered_values': requested_data,
                    'filters': filters,
                    'result': result
                }),
                status.HTTP_200_OK
            )
        else:
            response = make_response(
                jsonify({
                    'error': 'File not found'
                }),
                status.HTTP_404_NOT_FOUND
            )

        return response

    def post(self, file_id):
        
        form_data = request.form

        # TODO here will be implemented a logic of saving filtered data

        current_file_response = requests.get(f'http://127.0.0.1:5000/file/{file_id}')

        if current_file_response.status_code == 200:
            response = make_response(
                jsonify({
                    'file_id': file_id,
                    'filtered_values': form_data
                }),
                status.HTTP_200_OK
            )
        else:
            response = make_response(
                jsonify({
                    'error': 'File not found'
                }),
                status.HTTP_404_NOT_FOUND
            )

        return response


