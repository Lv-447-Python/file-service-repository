from flask import render_template, request
from flask.views import MethodView


import requests

import pandas as pd


class MyViewer(MethodView):

    def get(self):
        return render_template("viewer.html")

    def post(self): 
        #filtered_data = request.args.get('age', type=int)

        response_filters = requests.get('http://127.0.0.1:5000/filtering?file_id=50').json()['filters']

        print(response_filters)

        df = pd.read_csv(request.files.get('file'))
        #age = request.form.get('age')

        filtered_dict = request.form.to_dict()

        current_query = ''

        for key in filtered_dict:
            if filtered_dict[key] != '':
                current_query += """ and """ if current_query != '' else ''
                current_query += """{0} == '{1}'""".format(key, filtered_dict[key])


        length = len(current_query)
        print('Query:<', current_query, '>end', 'type of query:', type(current_query))
        filtered = df.query(current_query)

        return render_template('viewer.html', filters=response_filters,show=filtered.to_html())
