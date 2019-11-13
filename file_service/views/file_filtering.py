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




class FileFiltering(Resource):
 
    def get(self):

        return jsonify({
            'msg': 'GET'
        })

    def post(self):
        
        # if 'filefilter' not in request.files:
        #     return redirect(request.url)
        # file = request.files['filefilter']

        # # if user does not select file, browser also
        # # submit a empty part without filename
        # if file.filename == '' or not allowed_file(file.filename):
        #     return redirect(request.url)


        form_data = request.form


        #valentin_url = '127.0.0.1:5000/'
        #response = requests.put(valentin_url, data=jsonify(form_data))
        

        #filters = extract_filters(file)
 
        return jsonify({
            'form-data': form_data,
            'status': status.HTTP_200_OK
        })


  

    #TODO create resource hah