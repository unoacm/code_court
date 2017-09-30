from lxml import html

from base_test import BaseTest

import model
from database import db_session

class UsersTestCase(BaseTest):
    """
    Contains tests for the users blueprint
    """

    def _user_add(self, init_user_email):
        rv = self.app.post(
            '/admin/users/add/',
            data={
                "name": "Johnny Test",
                "email": init_user_email,
                "password": "password",
                "confirm_password": "password",
                "misc_data": "{}",
                "contest_ids": "",
                "user_role_ids": "",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to add user")

        rv = self.app.get('/admin/users/')
        root = html.fromstring(rv.data)
        page_user_emails = [x.text for x in root.cssselect(".user_email")]
        self.assertIn(init_user_email, page_user_emails, "User was not added")

    def _user_edit(self, old_email, new_email):
        user_id = model.User.query.filter_by(email=old_email).one().id

        rv = self.app.post(
            '/admin/users/add/',
            data={
                "user_id": user_id,
                "name": "Johnny Test",
                "email": new_email,
                "username": "",
                "password": "",
                "confirm_password": "",
                "misc_data": "{}",
                "contest_ids": "",
                "user_role_ids": "",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to edit user")

        rv = self.app.get('/admin/users/')
        root = html.fromstring(rv.data)
        page_user_emails = [x.text for x in root.cssselect(".user_email")]
        self.assertIn(new_email, page_user_emails, "User was not edited")

    def _user_del(self, email):
        user_id = model.User.query.filter_by(email=email).one().id

        rv = self.app.get(
            '/admin/users/del/{}'.format(user_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to delete user")

        rv = self.app.get('/admin/users/')
        root = html.fromstring(rv.data)
        page_user_emails = [x.text for x in root.cssselect(".user_email")]
        self.assertNotIn(email, page_user_emails, "User was not deleted")

    def test_user_crud(self):
        init_user_email = "micah287410@gmail.com"
        edit_user_email = "josiah12941@gmail.com"

        self.login("admin@example.org", "pass")

        self._user_add(init_user_email)
        self._user_edit(init_user_email, edit_user_email)
        self._user_del(edit_user_email)

