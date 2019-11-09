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

class FileFiltering(Resource):

    def get(self):
        return jsonify({
            'haha': 'benis'
        })

    def post(self):
        
        # hardcode mode: ON
        current_file_id = 23
        current_filters = {'color': 'red'}

        data = {
            'id': current_file_id,
            'filters': current_filters
        }

 
        return None



    #TODO create resource hah