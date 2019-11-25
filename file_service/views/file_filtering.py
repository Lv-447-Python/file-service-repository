import requests
import json
import pandas as pd

from flask import jsonify, request, make_response
from flask_api import status
from flask_restful import Resource

from file_service import API
from file_service import logging
from file_service.views.index import extract_headers

from functools import reduce


class FileFiltering(Resource):
    """Resource class for filtering loaded dataset"""

    @staticmethod
    def simple_query(data_frame, key, query_string):
        resulted_rows = data_frame.query("""{0} == '{1}'""".format(key, query_string))

        return resulted_rows

    @staticmethod
    def parse_part(string):

        count_start = string.find('{')
        count_end   = string.find('}')

        if count_start == -1 or count_end == -1:
            return string

        value = string[:count_start]

        amount = string[count_start + 1:count_end]

        is_percent = amount.find('%')

        if is_percent != -1:
            numb = amount[:is_percent]
        else:
            numb = amount

        return value, int(numb), is_percent != - 1

    @staticmethod
    def parse_request_filter(filter_query):
        is_complex = filter_query.find('&')

        if is_complex == -1:
            result = FileFiltering.parse_part(filter_query)
        else:
            result = [FileFiltering.parse_part(filter_value) for filter_value in filter_query.split('&')]

        return result

    @staticmethod
    def filter_dataset(file_path, requested_form):
        """Function for filtering dataset by requested form values"""
        try:
            data_frame = pd.read_csv(file_path, dtype=str)

            data_frame.columns = [cols.capitalize() for cols in data_frame]

            data_frame_size = data_frame.shape[0]

            indexes = [data_frame.index]

            for key in requested_form:
                if requested_form[key] != '':
                    query_parts = FileFiltering.parse_request_filter(requested_form[key])

                    if isinstance(query_parts, str):
                        resulted_rows = FileFiltering.simple_query(data_frame, key, query_parts)

                        indexes.append(resulted_rows.index)
                    else:
                        partials = []
                        for part in query_parts:
                            if isinstance(part, str):
                                resulted_rows = FileFiltering.simple_query(data_frame, key, part)

                                partials.append(resulted_rows)
                            else:
                                value, count, is_percent = part

                                rows_count = count if not is_percent else int(count * data_frame_size / 100)

                                partials.append(data_frame.query("""{0} == '{1}'""".format(key, value))[:rows_count])

                        if len(partials) > 0:
                            indexes.append(pd.concat(partials).index)


            final_indexes = list(reduce(lambda current, next_one: current & next_one, indexes))

            return data_frame.loc[final_indexes].to_json(orient='index')

        except ValueError:
            logging.error(f'Error to read file as csv by path: {file_path}')



    def get(self, file_id):

        file_response = requests.get(f'http://127.0.0.1:5000/file/{file_id}')

        if file_response.status_code == 200:
            current_file_path = file_response.json()['path']
            current_file_headers = extract_headers(current_file_path)

            response = make_response(
                jsonify({
                    'file_id': file_id,
                    'file_path': current_file_path,
                    'headers': current_file_headers,
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

            filters = extract_headers(current_file_path)

            result = json.loads(FileFiltering.filter_dataset(current_file_path, requested_data))

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


API.add_resource(FileFiltering, '/filtering/<int:file_id>')
