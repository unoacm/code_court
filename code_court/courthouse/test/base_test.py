import json
import logging
import unittest

from flask_login import current_user

import sqlalchemy

from web import app, setup_database

import model
from database import db_session, engine, Base

class BaseTest(unittest.TestCase):
    """
    Contains tests for the problems blueprint
    """

    def setUp(self):
        logging.disable(logging.CRITICAL)

        app.config['TESTING'] = True
        app.app_context().push()
        self.app = app.test_client()

        db_session.commit()
        Base.metadata.drop_all(engine)
        db_session.commit()
        Base.metadata.create_all(engine)
        db_session.commit()


        logging.info("Setting up database")
        setup_database(app)

    def login(self, email, password):
        with self.app:
            rv = self.app.post(
                '/admin/login',
                data=dict(email=email, password=password),
                follow_redirects=True)

            self.assertEqual(rv.status_code, 200, "Failed to login")
            self.assertNotEqual(current_user, None, "Failed to login")
            self.assertFalse(current_user.is_anonymous, "Failed to login")
            self.assertEqual(current_user.email, email, "Failed to login")

            return rv

    def logout(self):
        with self.app:
            rv = self.app.get('/admin/logout', follow_redirects=True)
            self.assertNotEqual(current_user, None, "Failed to logout")
            self.assertTrue(current_user.is_anonymous, "Failed to logout")

            return rv

    def get_jwt_token(self, email, password):
        rv = self.app.post('/api/login', data=json.dumps({
            "email": email,
            "password": password,
        }), content_type='application/json')
        j = json.loads(rv.data.decode("UTF-8"))
        return j['access_token']

    def jwt_get(self, url, auth_token=None, headers=None):
        if not headers:
            h = {}

        if auth_token:
            h["Authorization"] = "Bearer " + auth_token

        return self.app.get(url,
            headers=h,
            content_type='application/json',
            follow_redirects=True)

    def post_json(self, url, data, auth_token=None, headers=None):
        if not headers:
            h = {}

        if auth_token:
            h["Authorization"] = "Bearer " + auth_token

        return self.app.post(url,
            data=json.dumps(data),
            headers=h,
            content_type='application/json',
            follow_redirects=True)

    def tearDown(self):
        try:
            self.logout()
        except Exception:
            self.fail("Failed to logout")
        finally:
            db_session.commit()
            Base.metadata.drop_all(engine)
            db_session.commit()
            Base.metadata.create_all(engine)
            db_session.commit()

