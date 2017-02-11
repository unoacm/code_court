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
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        app.config['TESTING'] = True
        app.app_context().push()
        self.app = app.test_client()
        with app.app_context():
            web.setup_database(app)

    def test_language(self):
        """Tests language viewing, adding, editing, deleting"""

        init_lang_name = b"benscript45"
        edit_lang_name = b"josiahscript37"

        # check adding
        rv = self.app.post('/admin/languages/add/', data={
            "name": init_lang_name,
            "is_enabled": "on",
            "run_script": "#!/bin/bash\nruby $1",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        init_lang_count = rv.data.count(init_lang_name)

        self.assertEqual(init_lang_count, 1)

        # check editing
        rv = self.app.post('/admin/languages/add/', data={
            "lang_id": model.Language.query.all()[-1].id,
            "name": edit_lang_name,
            "is_enabled": "on",
            "run_script": "#!/bin/bash\njruby $1",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        edit_lang_count = rv.data.count(edit_lang_name)
        init_lang_count = rv.data.count(init_lang_name)

        self.assertEqual(edit_lang_count, 1)
        self.assertEqual(init_lang_count, 0)

        # check deleting
        rv = self.app.get('/admin/languages/del/2/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        self.assertEqual(rv.status_code, 200)
        edit_lang_count = rv.data.count(edit_lang_name)

        self.assertEqual(edit_lang_count, 0)

    def tearDown(self):
        model.db.drop_all()

if __name__ == '__main__':
    unittest.main()
