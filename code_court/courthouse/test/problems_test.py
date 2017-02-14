import os
import unittest
import tempfile

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

    def test_problems(self):
        """Tests problem viewing, adding, editing, deleting"""

        init_problem_name = b"sandwich123"
        edit_problem_name = b"sandwich456"
        # check adding
        rv = self.app.post('/admin/problems/add/', data={
            "problem_type_id": model.ProblemType.query.filter_by(name="input-output").one().id,
            "name": init_problem_name,
            "problem_statement": "## is there a problem here",
            "sample_input": "1",
            "sample_output": "2",
            "secret_input": "1 2 3 ",
            "secret_output": "4 5 6",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/problems/')
        self.assertEqual(rv.status_code, 200)
        init_problem_count = rv.data.count(init_problem_name)

        self.assertEqual(init_problem_count, 1)

        problem_id = model.Problem.query.all()[-1].id

        # check editing
        rv = self.app.post('/admin/problems/add/', data={
            "problem_id": problem_id,
            "problem_type_id": model.ProblemType.query.filter_by(name="input-output").one().id,
            "name": edit_problem_name,
            "problem_statement": "## is there a problem here",
            "sample_input": "1",
            "sample_output": "2",
            "secret_input": "1 2 3",
            "secret_output": "4 5 6",
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/problems/')
        self.assertEqual(rv.status_code, 200)
        edit_problem_count = rv.data.count(edit_problem_name)
        init_problem_count = rv.data.count(init_problem_name)

        self.assertEqual(edit_problem_count, 1)
        self.assertEqual(init_problem_count, 0)

        # check deleting
        rv = self.app.get('/admin/problems/del/' + str(problem_id) +'/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/admin/problems/')
        self.assertEqual(rv.status_code, 200)
        edit_problem_count = rv.data.count(edit_problem_name)

        self.assertEqual(edit_problem_count, 0)

    def tearDown(self):
        model.db.drop_all()

if __name__ == '__main__':
    unittest.main()
