from flask import render_template, request
from flask.views import MethodView

import pandas as pd


class MyViewer(MethodView):

    def get(self):
        return render_template("viewer.html")

    def post(self):
        df = pd.read_csv(request.files.get('file'))
        return render_template('viewer.html', show=df.to_html())
