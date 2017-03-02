from lxml import html

from base_test import BaseTest

from web import model

class ContestsTestCase(BaseTest):
    """
    Contains tests for the contests blueprint
    """
    def _contest_add(self, init_contest_name, emails):
        rv = self.app.post('/admin/contests/add/', data={
            "name": init_contest_name,
            "activate_time": "2017-01-01T12:00",
            "start_time": "2017-01-01T13:00",
            "freeze_time": "2017-01-01T14:00",
            "end_time": "2017-01-01T15:00",
            "deactivate_time": "2017-01-01T16:00",
            "is_public": "on",
            "users": '\n'.join(emails),
            "problems": model.Problem.query.one().name,
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to add contest")

        rv = self.app.get('/admin/contests/')
        root = html.fromstring(rv.data)
        page_contest_names = [x.text for x in root.cssselect(".contest_name")]
        self.assertIn(init_contest_name, page_contest_names, "Contest was not added")

    def _contest_edit(self, old_name, new_name, emails):
        contest_id = model.Contest.query.filter_by(name=old_name).one().id

        rv = self.app.post('/admin/contests/add/', data={
            "contest_id": contest_id,
            "name": new_name,
            "activate_time": "2017-01-01T12:00",
            "start_time": "2017-01-01T13:00",
            "freeze_time": "2017-01-01T14:00",
            "end_time": "2017-01-01T15:00",
            "deactivate_time": "2017-01-01T16:00",
            "is_public": "on",
            "users": '\n'.join(emails),
            "problems": model.Problem.query.one().name,
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to edit contest")

        rv = self.app.get('/admin/contests/')
        root = html.fromstring(rv.data)
        page_contest_names = [x.text for x in root.cssselect(".contest_name")]
        self.assertIn(new_name, page_contest_names, "Contest was not edited")

    def _contest_del(self, name):
        contest_id = model.Contest.query.filter_by(name=name).one().id

        rv = self.app.get('/admin/contests/del/{}'.format(contest_id), follow_redirects=True)
        self.assertEqual(rv.status_code, 200, "Failed to delete contest")

        rv = self.app.get('/admin/contests/')
        root = html.fromstring(rv.data)
        page_contest_names = [x.text for x in root.cssselect(".contest_name")]
        self.assertNotIn(name, page_contest_names, "Contest was not deleted")

    def test_contest_crud(self):
        init_contest_name = "I see pea sea"
        edit_contest_name = "7er0 t1m3 4 s3gf4ult5"

        self.login("admin@example.org", "pass")

        # Need to have a problem to test a contest:
        self.app.post('/admin/problems/add/', data={
            "problem_type_id": model.ProblemType.query.filter_by(name="input-output").one().id,
            "slug": "2plus2",
            "name": "2 + 2",
            "problem_statement": "## is there a problem here",
            "sample_input": "1",
            "sample_output": "2",
            "secret_input": "1 2 3",
            "secret_output": "4 5 6",
        }, follow_redirects=True)

        # Add test contestants:
        roles = {x.id: x for x in model.UserRole.query.all()}
        names = ["Fred", "George", "Jenny", "Sam", "Jo", "Joe", "Sarah", "Ben", "Josiah", "Micah"]
        emails = ["testuser{}@example.org".format(i) for i in range(1,11)]

        for i in range(1,11):
            test_contestant = model.User(emails[i-1], names[i-1], "pass", user_roles=[roles['defendant']])
            model.db.session.add(test_contestant)

        self._contest_add(init_contest_name, emails[0:7])
        self._contest_edit(init_contest_name, edit_contest_name, emails[0:7])
        self._contest_del(edit_contest_name)
