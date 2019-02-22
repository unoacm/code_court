from lxml import html

from base_test import BaseTest

import model
from database import db_session


class ClarificationsTestCase(BaseTest):
    """
    Contains tests for the clarifications blueprint
    """

    def _clar_add(self, init_clar_problem, init_clar_subject, init_clar_user):
        rv = self.app.post(
            "/admin/clarifications/add/",
            data={
                "problem": init_clar_problem,
                "subject": init_clar_subject,
                "contents": "contents",
            },
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200, "Failed to add clarification")

        rv = self.app.get("/admin/clarifications/")
        root = html.fromstring(rv.data)
        page_clar_subjects = [x.text for x in root.cssselect(".clar_subject")]
        self.assertIn(
            init_clar_subject, page_clar_subjects, "Clarification was not added to page"
        )

    def _clar_answer(self, init_clar_problem, init_clar_subject):
        clar_id = (
            model.Clarification.query.filter_by(subject=init_clar_subject).one().id
        )
        rv = self.app.post(
            "/admin/clarifications/answer/{}".format(clar_id),
            data={
                "problem": init_clar_problem,
                "subject": init_clar_subject,
                "contents": "contents",
                "answer": "answer",
                "is_public": "True",
            },
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200, "Failed to answer clarification")

        rv = self.app.get("/admin/clarifications/")
        root = html.fromstring(rv.data)
        page_clar_answereds = [x.text for x in root.cssselect(".green")]
        self.assertIn(
            u"\u2713",
            page_clar_answereds,
            "Clarification was not successfully answered",
        )

    def _clar_del(self, init_clar_subject):
        clar_id = (
            model.Clarification.query.filter_by(subject=init_clar_subject).one().id
        )
        rv = self.app.get(
            "/admin/clarifications/del/{}".format(clar_id), follow_redirects=True
        )
        self.assertEqual(rv.status_code, 200, "Failed to delete clarification")

        rv = self.app.get("admin/clarifications/")
        root = html.fromstring(rv.data)
        page_clar_subjects = [x.text for x in root.cssselect(".clar_subject")]
        self.assertFalse(page_clar_subjects)

    def test_clar_crud(self):
        test_prob = model.Problem(
            model.ProblemType.query.filter_by(name="input-output").one(),
            "initprob",
            "init_problem_name",
            "## is there a problem here",
            "1",
            "2",
            "1 2 3",
            "4 5 6",
        )
        db_session.add(test_prob)
        db_session.commit()

        init_clar_problem = model.Problem.query.first().name
        init_clar_subject = "the test"
        init_clar_user = model.User.query.first()

        self.login("admin", "pass")

        self._clar_add(init_clar_problem, init_clar_subject, init_clar_user)
        self._clar_answer(init_clar_problem, init_clar_subject)
        self._clar_del(init_clar_subject)
