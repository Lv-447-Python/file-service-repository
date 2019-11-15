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
import pandas as pd


from requests.exceptions import HTTPError


from file_service.views.index import extract_filters


class FileFiltering(Resource):
    
    @staticmethod
    def get_filtered_data(file_path, test_filter):
        pass
    

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

        

        return jsonify({
            'filtered_values': requested_data,
            'filters': filters,
            'status': status.HTTP_200_OK
        })

    def post(self):
        
        form_data = request.form


        # #valentin_url = '127.0.0.1:5000/'
        # #response = requests.put(valentin_url, data=jsonify(form_data))
        

        # #filters = extract_filters(file)

        # filtered_rows_id = FileFiltering.filter_by_values(form_data) 

        # try:
        #     history_url = 'http://127.0.0.1:5000/'
        #     put_rows_id_to_history_response = requests.put(history_url, data=filtered_rows_id)
        # except HTTPError as err:
        #     print('Error, can not save your filters: ', err)

        
        # if put_rows_id_to_history_response.status_code == 200:
        current_file_id = request.args.get('file_id')

        return jsonify({
            'file_id': current_file_id,
            'form_data': form_data,
            'status': status.HTTP_200_OK })
    

    
   



  

    #TODO create resource hah