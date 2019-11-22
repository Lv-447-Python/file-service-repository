import io
import json
import logging

from file_service import app, db
import unittest

POSTGRES = {
    'user': 'postgres',
    'pw': '02082001',
    'db': 'statcrutch_test',
    'host': '127.0.0.1',
    'port': '5432',
}

logging.getLogger().setLevel(logging.DEBUG)
logging.debug("-" * 20)


class MyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
        app.config['UPLOAD_FOLDER'] = 'upload_folder/'
        self.app = app.test_client()
        db.create_all()

    def test_base_service(self):
        response = self.app.get('/')
        assert response.status == '200 OK'

    def test_upload_file_using_string(self):
        test_data = b'Hello,World,Test,Flask'
        string = ","
        response = self.app.post('/',
                                 content_type='multipart/form-data',
                                 data={'user_file': (io.BytesIO(test_data), 'test.csv')})
        testing_data = json.loads(response.data)
        assert string.join(testing_data["filters"]) == test_data.decode('utf-8')
        assert response.status == '201 CREATED'

    def test_upload_file_using_file(self):
        with open('files_for_test/Test_dataset_filterMe.csv', 'rb') as file_test:
            binary_file_test = file_test.read()

        with io.BytesIO(binary_file_test) as testing_file:
            response = self.app.post('/',
                                     content_type='multipart/form-data',
                                     data={'user_file': (testing_file, 'test1.csv')})

        assert response.status == '201 CREATED'

    def test_hash_and_size(self):
        pass

    def test_find_file(self):
        pass

    def test_delete_file(self):
        pass

    def test_read_data_from_file(self):
        pass

    def test_read_column_names_in_data(self):
        pass

    def test_filter_data(self):
        pass


if __name__ == '__main__':
    unittest.main()
