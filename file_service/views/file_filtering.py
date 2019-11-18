import os

from flask_api import status
from flask_restful import Resource

from file_service import app, db, api
from file_service.models.file import File
from file_service.serializers.file_schema import FileSchema

from werkzeug.utils import secure_filename, redirect
from flask import jsonify, request, render_template, session


import requests
import hashlib
import datetime
import csv
import json
import pandas as pd


from requests.exceptions import HTTPError


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


            filtered   = df.query(current_query) if current_query != '' else df

            result     = filtered.to_json(orient='index')
   
            return result
        except Exception as err:
            print('Smth gone wrong, ', err)
    

    def get(self):
        current_file_id      = request.args.get('file_id')

        current_file_path    = requests.get(f'http://127.0.0.1:5000/file?file_id={current_file_id}').json()['path']

        current_file_filters = extract_filters(current_file_path)


        return jsonify({
            'file_id': current_file_id,
            'file_path': current_file_path,
            'filters': current_file_filters,
            'status': status.HTTP_200_OK
        })

    def put(self):
        requested_data    = request.form

        current_file_id   = request.args.get('file_id')

        current_file_path = requests.get(f'http://127.0.0.1:5000/file?file_id={current_file_id}').json()['path']

        filters = extract_filters(current_file_path)

        result  = json.loads(FileFiltering.filter_dataset(current_file_path, requested_data))

        return jsonify({
            'filtered_values': requested_data,
            'filters': filters,
            'result': result,
            'status': status.HTTP_200_OK
        })

    def post(self):
        
        form_data = request.form

        current_file_id = request.args.get('file_id')

        return jsonify({
            'file_id': current_file_id,
            'form_data': form_data,
            'status': status.HTTP_200_OK })
