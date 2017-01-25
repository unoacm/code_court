import os
import unittest
import tempfile

import web

from web import app, model

class LanguageTestCase(unittest.TestCase):
    """
    Contains tests for the languages blueprint
    """
    def setUp(self):
        self.db_fd, self.dbfile = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + self.dbfile
        app.config['TESTING'] = True
        app.app_context().push()
        self.app = app.test_client()
        with app.app_context():
            web.setup_database(app)

    def test_language(self):
        """Tests language viewing, adding, editing, deleting"""

        init_python_name = b"python2.7"
        edit_python_name = b"python3.6"

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        initial_python_count = rv.data.count(init_python_name)

        # check adding
        rv = self.app.post('/admin/languages/add/', data={
            "name": init_python_name,
            "is_enabled": "on"
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        add_python_count = rv.data.count(init_python_name)
        init_python3_count = rv.data.count(edit_python_name)

        self.assertEqual(add_python_count, initial_python_count+1)

        # check editing
        rv = self.app.post('/admin/languages/add/', data={
            "lang_id": 1,
            "name": edit_python_name,
            "is_enabled": "on"
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        edit_python_count = rv.data.count(init_python_name)
        edit_python3_count = rv.data.count(edit_python_name)

        self.assertEqual(edit_python_count, initial_python_count)
        self.assertEqual(edit_python3_count, init_python3_count+1)

        # check deleting
        rv = self.app.get('/admin/languages/del/1/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        del_python_count = rv.data.count(edit_python_name)

        self.assertEqual(initial_python_count, del_python_count)
        self.assertEqual(add_python_count-1, del_python_count)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.dbfile)

if __name__ == '__main__':
    unittest.main()
