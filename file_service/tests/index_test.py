import unittest

from file_service import app, db


class IndexTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False

        self.app = app.test_client()
    
    def tearDown(self):
        pass

    def test_index_status(self):
        response = self.app.get('/')

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()



