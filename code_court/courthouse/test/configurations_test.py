from lxml import html

from base_test import BaseTest

import model
from database import db_session

class ConfigurationsTestCase(BaseTest):
    """
    Contains tests for the configurations blueprint
    """

    def _config_add(self, init_config_key):
        rv = self.app.post(
            '/admin/configurations/add/',
            data={
                "key": init_config_key,
                "val": "True",
                "valType": "bool",
                "category": "admin",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to add configuration")

        rv = self.app.get('/admin/configurations/')
        root = html.fromstring(rv.data)
        page_config_keys = [x.text for x in root.cssselect(".config_key")]
        self.assertIn(init_config_key, page_config_keys,
                      "Configuration was not added")

    def _config_edit(self, old_key, new_key):
        config_id = model.Configuration.query.filter_by(key=old_key).one().id

        rv = self.app.post(
            '/admin/configurations/add/',
            data={
                "config_id": config_id,
                "key": new_key,
                "val": "True",
                "valType": "bool",
                "category": "admin",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to edit configuration")

        rv = self.app.get('/admin/configurations/')
        root = html.fromstring(rv.data)
        page_config_keys = [x.text for x in root.cssselect(".config_key")]
        self.assertIn(new_key, page_config_keys,
                      "Configuration was not edited")

    def _config_del(self, key):
        config_id = model.Configuration.query.filter_by(key=key).one().id

        rv = self.app.get(
            '/admin/configurations/del/{}'.format(config_id),
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to delete configuration")

        rv = self.app.get('/admin/configurations/')
        root = html.fromstring(rv.data)
        page_config_keys = [x.text for x in root.cssselect(".config_key")]
        self.assertNotIn(key, page_config_keys,
                         "Configuration was not deleted")

    def test_configuration_crud(self):
        init_config_key = "init_config_125r32"
        edit_config_key = "edit_config_08294e"

        self.login("admin", "pass")

        self._config_add(init_config_key)
        self._config_edit(init_config_key, edit_config_key)
        self._config_del(edit_config_key)

