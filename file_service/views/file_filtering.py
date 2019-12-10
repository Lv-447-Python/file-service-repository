"""File filtering module"""
from functools import reduce
import json
import pandas as pd

from flask import jsonify, request, make_response
from flask_api import status
from flask_restful import Resource

from file_service import API

from file_service.views.index import extract_headers, file_finding_handler
from file_service.models.file import File
from file_service.logger.logger import LOGGER


class FileFiltering(Resource):
    """
    Resource for filtering loaded data set
    methods:
        GET: host/file/<int:file_id>  ==> return file metadata by file_id
        PUT: host/file/<int:file_id>  ==> return filtered dataset
        POST: host/file/<int:file_id> ==> return filtered dataset id's and form values
    """

    @staticmethod
    def parse_part(string):
        """
        Function for parsing single string
        Args:
            string (str):
        Returns:
            tuple if string with special symbols, str otherwise
        """
        count_start = string.find('{')
        count_end = string.find('}')

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
    def parse_query_string(query):
        """
        Function for parsing query
        Args:
            query (str):
        Returns:
            list if query is complex, result of function parse_part otherwise
        """
        is_complex = query.find('&')

        if is_complex == -1:
            result = FileFiltering.parse_part(query)
        else:
            result = [FileFiltering.parse_part(filter_value) for filter_value in query.split('&')]

        return result

    @staticmethod
    def filter_dataset(file_path, headers, filter_data):
        """
        Function for filtering data set by filtering data values
        Args:
            file_path (str):
            headers (list):
            filter_data (dict):
        Returns:
            pandas's data frame object
        """
        try:
            data_frame = pd.read_csv(file_path, dtype=str)
        except ValueError:
            LOGGER.error(f'Error to read file as csv by path: {file_path}')

        data_frame.columns = [cols.capitalize() for cols in data_frame]

        data_frame_size = data_frame.shape[0]

        indexes = []

        for header in headers:
            resulted_str = ''
            current_key_number = 1

            for key in filter_data:
                if filter_data[key] == '':
                    continue

                if header in key:
                    if int(key.split(header)[1][0]) != current_key_number:
                        current_key_number += 1
                        resulted_str += '&'

                    is_count = 'count' in key
                    if is_count:  # input with value
                        try:
                            count = str(filter_data[key]) if str(filter_data[key]) != '' else data_frame_size
                        except ValueError:
                            LOGGER.error('Field expected to be string type')
                        resulted_str += '{' + str(count) + '}'
                    else:  # input with count
                        resulted_str += filter_data[key]

            if resulted_str == '':
                continue
            LOGGER.info(resulted_str)
            query_parts = FileFiltering.parse_query_string(resulted_str)

            if isinstance(query_parts, tuple):
                value, count, is_percent = query_parts

                filtered_result = data_frame.query(f"""{header} == '{value}'""")

                rows_count = count if not is_percent else int(count * len(filtered_result) / 100)

                indexes.append((set(filtered_result.index), rows_count))
            elif isinstance(query_parts, str):

                filtered_result = data_frame.query(f"""{header} == '{query_parts}'""")

                indexes.append((set(filtered_result.index), data_frame_size))
            else:
                partials = []
                for part in query_parts:

                    if isinstance(part, str):

                        filtered_result = data_frame.query(f"""{header} == '{part}'""")

                        partials.append(filtered_result)
                    else:
                        value, count, is_percent = part

                        filtered_result = data_frame.query(f"""{header} == '{value}'""")

                        rows_count = count if not is_percent else int(count * len(filtered_result) / 100)

                        partials.append(filtered_result[:rows_count])

                if len(partials) > 0:
                    concatenated_indexes = pd.concat(partials).index
                    indexes.append((set(concatenated_indexes), len(concatenated_indexes)))

        sorted_indexes = sorted(indexes, key=lambda x: x[1], reverse=True)
        LOGGER.info(sorted_indexes)

        for index_list in sorted_indexes:
            working_indexes, working_amount = index_list

            LOGGER.info(f'Indexes: {working_indexes}, AMOUNT: {working_amount}')
            data_frame = data_frame.loc[data_frame.index & working_indexes][:working_amount]

        return data_frame

    @file_finding_handler
    def get(self, file_id):
        """GET method, for getting file metadata by file_id"""
        requested_file = File.query.filter_by(id=file_id).first()

        try:
            current_file_path = requested_file.file_path
            current_file_headers = extract_headers(current_file_path)

            response = make_response(
                jsonify({
                    'file_id': file_id,
                    'path': current_file_path,
                    'headers': current_file_headers,
                    'message': 'Success'
                }),
                status.HTTP_200_OK
            )
            return response

        except AttributeError:
            LOGGER.error(f'File with id: {file_id}, not found')
            return None

    @file_finding_handler
    def put(self, file_id):
        """PUT method for filtering current dataset"""
        requested_data = request.form

        requested_file = File.query.filter_by(id=file_id).first()

        try:
            current_file_path = requested_file.file_path
            current_file_headers = extract_headers(current_file_path)

            result = json.loads(
                FileFiltering.filter_dataset(file_path=current_file_path,
                                             headers=current_file_headers,
                                             filter_data=requested_data
                                             ).to_json(orient='index')
            )

            response = make_response(
                jsonify({
                    'filtered_values': requested_data,
                    'result': result
                }),
                status.HTTP_200_OK
            )

            return response

        except AttributeError:
            LOGGER.error(f'File with id: {file_id}, not found')
            return None

    @file_finding_handler
    def post(self, file_id):
        """POST method for saving filtered data set into history"""
        form_data = request.form

        requested_file = File.query.filter_by(id=file_id).first()

        try:
            current_file_path = requested_file.file_path

            current_file_headers = extract_headers(current_file_path)

            resulted_indexes = FileFiltering.filter_dataset(current_file_path, current_file_headers,
                                                            form_data).index

            response = make_response(
                jsonify({
                    'file_id': file_id,
                    'filter_values': form_data,
                    'resulted_indexes': resulted_indexes
                }),
                status.HTTP_200_OK
            )
        except AttributeError:
            LOGGER.error(f'File with id: {file_id}, not found')
            return None

        return response


API.add_resource(FileFiltering, '/filtering/<int:file_id>')
