import os
import unittest
import tempfile

from lxml import html

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

    def _lang_add(self, init_lang_name):
        rv = self.app.post('/admin/languages/add/', data={
            "name": init_lang_name,
            "is_enabled": "on",
            "run_script": "#!/bin/bash\nruby $1",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        root = html.fromstring(rv.data)
        page_lang_names = [x.text for x in root.cssselect(".lang_name")]
        self.assertIn(init_lang_name, page_lang_names)

    def _lang_edit(self, old_name, new_name):
        lang_id = model.Language.query.filter_by(name=old_name).one().id

        rv = self.app.post('/admin/languages/add/', data={
            "lang_id": lang_id,
            "name": new_name,
            "is_enabled": "on",
            "run_script": "#!/bin/bash\nruby $1",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        root = html.fromstring(rv.data)
        page_lang_names = [x.text for x in root.cssselect(".lang_name")]
        self.assertIn(new_name, page_lang_names)

    def _lang_del(self, name):
        lang_id = model.Language.query.filter_by(name=name).one().id

        rv = self.app.get('/admin/languages/del/{}'.format(lang_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/languages/')
        root = html.fromstring(rv.data)
        page_lang_names = [x.text for x in root.cssselect(".lang_name")]
        self.assertNotIn(name, page_lang_names)


    def test_language_crud(self):
        init_lang_name = "benscript49495885"
        edit_lang_name = "josiahscript31231137"

        self._lang_add(init_lang_name)
        self._lang_edit(init_lang_name, edit_lang_name)
        self._lang_del(edit_lang_name)

    def tearDown(self):
        model.db.drop_all()

if __name__ == '__main__':
    unittest.main()
