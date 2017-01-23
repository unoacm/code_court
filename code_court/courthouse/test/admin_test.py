import os
import unittest
import tempfile

import web

from web import app, model

class AdminTestCase(unittest.TestCase):
    """
    Contains tests for the database model
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
        """Tests language viewing, adding, deleting"""

        rv = self.app.get('/admin/languages/')
        initial_python_count = rv.data.count(b"python")

        # add python
        add_rv = self.app.post('/admin/languages/add/', data={
            "name": "python",
            "is_enabled": "on"
        }, follow_redirects=True)

        check_add_rv = self.app.get('/admin/languages/')


        # check that python is added
        check_add_rv = self.app.get('/admin/languages/')
        add_python_count = check_add_rv.data.count(b"python")
        self.assertEqual(add_python_count, initial_python_count+1)

        # delete python
        del_rv = self.app.get('/admin/languages/del/1')

        # check that python is deleted
        check_del_rv = self.app.get('/admin/languages/')
        del_python_count = check_del_rv.data.count(b"python")
        self.assertEqual(initial_python_count, del_python_count)
        self.assertEqual(add_python_count-1, del_python_count)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.dbfile)

if __name__ == '__main__':
    unittest.main()
