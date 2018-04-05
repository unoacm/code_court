from lxml import html

from base_test import BaseTest

import model
from database import db_session

class LanguagesTestCase(BaseTest):
    """
    Contains tests for the languages blueprint
    """

    def _lang_add(self, init_lang_name):
        rv = self.app.post(
            '/admin/languages/add/',
            data={
                "name": init_lang_name,
                "syntax_mode": "ruby",
                "is_enabled": "on",
                "run_script": "#!/bin/bash\nruby $1",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to add language")

        rv = self.app.get('/admin/languages/')
        root = html.fromstring(rv.data)
        page_lang_names = [x.text for x in root.cssselect(".lang_name")]
        self.assertIn(init_lang_name, page_lang_names,
                      "Language was not added")

    def _lang_edit(self, old_name, new_name):
        lang_id = model.Language.query.filter_by(name=old_name).one().id

        rv = self.app.post(
            '/admin/languages/add/',
            data={
                "lang_id": lang_id,
                "name": new_name,
                "syntax_mode": "ruby",
                "is_enabled": "on",
                "run_script": "#!/bin/bash\nruby $1",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to edit language")

        rv = self.app.get('/admin/languages/')
        root = html.fromstring(rv.data)
        page_lang_names = [x.text for x in root.cssselect(".lang_name")]
        self.assertIn(new_name, page_lang_names, "Language was not edited")

    def _lang_del(self, name):
        lang_id = model.Language.query.filter_by(name=name).one().id

        rv = self.app.get(
            '/admin/languages/del/{}'.format(lang_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to delete language")

        rv = self.app.get('/admin/languages/')
        root = html.fromstring(rv.data)
        page_lang_names = [x.text for x in root.cssselect(".lang_name")]
        self.assertNotIn(name, page_lang_names, "Language was not deleted")

    def test_language_crud(self):
        init_lang_name = "benscript49495885"
        edit_lang_name = "josiahscript31231137"

        self.login("admin", "pass")

        self._lang_add(init_lang_name)
        self._lang_edit(init_lang_name, edit_lang_name)
        self._lang_del(edit_lang_name)

