from lxml import html

from base_test import BaseTest

import model
from database import db_session

class ProblemsTestCase(BaseTest):
    """
    Contains tests for the problems blueprint
    """

    def _problem_add(self, init_problem_name):
        rv = self.app.post(
            '/admin/problems/add/',
            data={
                "problem_type_id":
                model.ProblemType.query.filter_by(
                    name="input-output").one().id,
                "slug":
                "initprob",
                "name":
                init_problem_name,
                "problem_statement":
                "## is there a problem here",
                "sample_input":
                "1",
                "sample_output":
                "2",
                "secret_input":
                "1 2 3",
                "secret_output":
                "4 5 6",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to add problem")

        rv = self.app.get('/admin/problems/')
        root = html.fromstring(rv.data)
        page_problem_names = [x.text for x in root.cssselect(".problem_name")]
        self.assertIn(init_problem_name, page_problem_names,
                      "Problem was not added")

    def _problem_edit(self, old_name, new_name):
        problem_id = model.Problem.query.filter_by(name=old_name).one().id

        rv = self.app.post(
            '/admin/problems/add/',
            data={
                "problem_id":
                problem_id,
                "problem_type_id":
                model.ProblemType.query.filter_by(
                    name="input-output").one().id,
                "slug":
                "initprob",
                "name":
                new_name,
                "problem_statement":
                "## there is a problem here",
                "sample_input":
                "1",
                "sample_output":
                "2",
                "secret_input":
                "1 2 3",
                "secret_output":
                "4 5 6",
            },
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to edit problem")

        rv = self.app.get('/admin/problems/')
        root = html.fromstring(rv.data)
        page_problem_names = [x.text for x in root.cssselect(".problem_name")]
        self.assertIn(new_name, page_problem_names, "Problem was not edited")

    def _problem_del(self, name):
        problem_id = model.Problem.query.filter_by(name=name).one().id

        rv = self.app.get(
            '/admin/problems/del/{}'.format(problem_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to delete problem")

        rv = self.app.get('/admin/problems/')
        root = html.fromstring(rv.data)
        page_problem_names = [x.text for x in root.cssselect(".problem_name")]
        self.assertNotIn(name, page_problem_names, "Problem was not deleted")

    def test_problem_crud(self):
        init_problem_name = "fibbonaci49495885"
        edit_problem_name = "shortestpath31231137"

        self.login("admin@example.org", "pass")

        self._problem_add(init_problem_name)
        self._problem_edit(init_problem_name, edit_problem_name)
        self._problem_del(edit_problem_name)

