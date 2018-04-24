from lxml import html

from base_test import BaseTest

import model
from database import db_session

class UsersTestCase(BaseTest):
    """
    Contains tests for the users blueprint
    """

    def _user_add(self, init_user_username):
        rv = self.app.post(
            '/admin/users/add/',
            data={
                "name": "Johnny Test",
                "username": init_user_username,
                "password": "password",
                "confirm_password": "password",
                "misc_data": "{}",
                "contest_names": "",
                "user_roles": "",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to add user")

        rv = self.app.get('/admin/users/')
        root = html.fromstring(rv.data)
        page_user_usernames = [x.text for x in root.cssselect(".user_username")]
        self.assertIn(init_user_username, page_user_usernames, "User was not added")

    def _user_edit(self, old_username, new_username):
        user_id = model.User.query.filter_by(username=old_username).one().id

        rv = self.app.post(
            '/admin/users/add/',
            data={
                "user_id": user_id,
                "name": "Johnny Test",
                "username": new_username,
                "password": "",
                "confirm_password": "",
                "misc_data": "{}",
                "contest_names": "",
                "user_roles": "",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to edit user")

        rv = self.app.get('/admin/users/')
        root = html.fromstring(rv.data)
        page_user_usernames = [x.text for x in root.cssselect(".user_username")]
        self.assertIn(new_username, page_user_usernames, "User was not edited")

    def _user_del(self, username):
        user_id = model.User.query.filter_by(username=username).one().id

        rv = self.app.get(
            '/admin/users/del/{}'.format(user_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to delete user")

        rv = self.app.get('/admin/users/')
        root = html.fromstring(rv.data)
        page_user_usernames = [x.text for x in root.cssselect(".user_username")]
        self.assertNotIn(username, page_user_usernames, "User was not deleted")

    def test_user_crud(self):
        init_user_username = "micah287410"
        edit_user_username = "josiah12941"

        self.login("admin", "pass")

        self._user_add(init_user_username)
        self._user_edit(init_user_username, edit_user_username)
        self._user_del(edit_user_username)

