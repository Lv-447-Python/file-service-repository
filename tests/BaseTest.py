# NOTE: Don't run it via IDE, but on terminal!

import io
import json
import unittest

from file_service.views.index import *

POSTGRES = {
    'user': 'postgres',
    'pw': '02082001',
    'db': 'statcrutch_test',
    'host': '127.0.0.1',
    'port': '5432',
}


class MyTestCase(unittest.TestCase):
    def setUp(self):
        APP.config['TESTING'] = True
        APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
        APP.config['UPLOAD_FOLDER'] = 'tests/upload_folder/'
        self.APP = APP.test_client()
        DB.create_all()

    def test_base_service(self):
        response = self.APP.get('/files')
        self.assertEqual(response.status, "200 OK")

    def test_upload_file_using_string(self):
        test_data = b'Hello,World,Test,Flask'
        string = ","
        response = self.APP.post('/files',
                                 content_type='multipart/form-data',
                                 data={'user_file': (io.BytesIO(test_data), '/test.csv')})
        testing_data = json.loads(response.data)
        self.assertEqual(string.join(testing_data["filters"]), test_data.decode('utf-8'))
        self.assertEqual(response.status, '201 CREATED')

    def test_upload_file_using_file(self):
        print(os.getcwd())
        with open('tests/test_files/Test_dataset_filterMe.csv', 'rb') as file_test:
            binary_file_test = file_test.read()

        with io.BytesIO(binary_file_test) as testing_file:
            response = self.APP.post('/files',
                                     content_type='multipart/form-data',
                                     data={'user_file': (testing_file, '/Test_dataset_filterMe.csv')})
        self.assertEqual(response.status, '201 CREATED')

    def test_find_file(self):
        response = self.APP.get('/files')
        get_all_id = list(map(lambda all_id: all_id["id"], json.loads(response.data)['all_files']))
        for id in get_all_id:
            response_id = self.APP.get('/file/' + str(id))
            self.assertEqual(response_id.status, '200 OK')
        self.assertEqual(response.status, '200 OK')

    def test_delete_file(self):
        with open('tests/test_files/Test_dataset_filterMe.csv', 'rb') as file_test:
            binary_test_file = file_test.read()
        with io.BytesIO(binary_test_file) as testing_file:
            response = self.APP.post('/files',
                                     content_type='multipart/form-data',
                                     data={'user_file': (testing_file, '/file_for_delete_from_db.csv')})
        self.assertEqual(response.status, '201 CREATED')
        response_delete = self.APP.delete('/file/' + str(json.loads(response.data)['data']['id']))
        self.assertEqual(response_delete.status, '200 OK')
        response_delete = self.APP.delete('/file/' + str(json.loads(response.data)['data']['id']))
        self.assertEqual(response_delete.status, '404 NOT FOUND')


if __name__ == '__main__':
    unittest.main()
