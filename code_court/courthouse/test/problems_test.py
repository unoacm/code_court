import os
import unittest
import tempfile

from lxml import html

import web

from web import app, model

class ProblemsTestCase(unittest.TestCase):
    """
    Contains tests for the problems blueprint
    """
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        app.config['TESTING'] = True
        app.app_context().push()
        self.app = app.test_client()
        with app.app_context():
            web.setup_database(app)

    def _problem_add(self, init_problem_name):
        rv = self.app.post('/admin/problems/add/', data={
            "problem_type_id": model.ProblemType.query.filter_by(name="input-output").one().id,
            "name": init_problem_name,
            "problem_statement": "## is there a problem here",
            "sample_input": "1",
            "sample_output": "2",
            "secret_input": "1 2 3",
            "secret_output": "4 5 6",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/problems/')
        root = html.fromstring(rv.data)
        page_problem_names = [x.text for x in root.cssselect(".problem_name")]
        self.assertIn(init_problem_name, page_problem_names)

    def _problem_edit(self, old_name, new_name):
        problem_id = model.Problem.query.filter_by(name=old_name).one().id

        rv = self.app.post('/admin/problems/add/', data={
            "problem_id": problem_id,
            "problem_type_id": model.ProblemType.query.filter_by(name="input-output").one().id,
            "name": new_name,
            "problem_statement": "## there is a problem here",
            "sample_input": "1",
            "sample_output": "2",
            "secret_input": "1 2 3",
            "secret_output": "4 5 6",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/problems/')
        root = html.fromstring(rv.data)
        page_problem_names = [x.text for x in root.cssselect(".problem_name")]
        self.assertIn(new_name, page_problem_names)

    def _problem_del(self, name):
        problem_id = model.Problem.query.filter_by(name=name).one().id

        rv = self.app.get('/admin/problems/del/{}'.format(problem_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/problems/')
        root = html.fromstring(rv.data)
        page_problem_names = [x.text for x in root.cssselect(".problem_name")]
        self.assertNotIn(name, page_problem_names)

    def test_problem_crud(self):
        init_problem_name = "fibbonaci49495885"
        edit_problem_name = "shortestpath31231137"

        self._problem_add(init_problem_name)
        self._problem_edit(init_problem_name, edit_problem_name)
        self._problem_del(edit_problem_name)

    def tearDown(self):
        model.db.drop_all()

if __name__ == '__main__':
    unittest.main()
