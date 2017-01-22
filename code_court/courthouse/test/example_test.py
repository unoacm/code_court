import os
import unittest
import tempfile

import web

from web import app

class ExampleTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            web.setup_database(app)

    def test_title(self):
        rv = self.app.get('/')
        assert b'code_court' in rv.data

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
