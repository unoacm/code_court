import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

test_case_problem_at = db.Table('test_case_problem', db.Model.metadata,
    db.Column('problem_id', db.Integer, db.ForeignKey('problem.id')),
    db.Column('test_case_id', db.Integer, db.ForeignKey('test_case.id'))
)


class Language(db.Model):
    """Stores the configuration for a programming language"""
    __tablename__ = 'language'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, unique=True, nullable=False)
    """str: the language name"""

    is_enabled = db.Column(db.Boolean, nullable=False)
    """bool: whether or not the language is enabled"""

    run_script = db.Column(db.String, nullable=False)
    """str: script (with shebang) that compiles and runs scripts for this language"""

    def __init__(self, name, is_enabled, run_script):
        self.name = name
        self.is_enabled = is_enabled
        self.run_script = run_script

    def __str__(self):
        return "Problem({})".format(self.name)


class Problem(db.Model):
    __tablename__ = 'problem'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    problem_statements = db.relationship("TestCase", secondary=test_case_problem_at, back_populates="problems")

    def __str__(self):
        return "Problem({})".format(self.name)

class TestCase(db.Model):
    __tablename__ = 'test_case'

    id = db.Column(db.Integer, primary_key=True)
    input_string = db.Column(db.String)
    output_string = db.Column(db.String)
    problems = db.relationship("Problem", secondary=test_case_problem_at, back_populates="problem_statements")
