import json
import datetime

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


class ProblemType(db.Model):
    """Stores information about a problem type"""
    __tablename__ = 'problem_type'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, unique=True, nullable=False)
    """str: the name of the problem type"""

    eval_script = db.Column(db.String, nullable=False)
    """str: script (with shebang) that evaluates this problem type"""

    def __init__(self, name, eval_script):
        self.name = name
        self.eval_script = eval_script


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


class User(db.Model):
    """Stores information about a user"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    """str: the user's email"""

    name = db.Column(db.String, nullable=False)
    """str: the user's full name, no specific format is assumed"""

    password = db.Column(db.String, nullable=False)
    """str: a hash of the user's password"""

    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    """str: the creation time of the user"""

    misc_data = db.Column(db.String, nullable=False)
    """str: misc data about a user, stored as a json object"""

    def __init__(self, email, name, password, creation_time=None, misc_data=None):
        if misc_data is None:
            misc_data = json.dumps({})

        if creation_time is None:
            self.creation_time = datetime.datetime.utcnow()

        self.email = email
        self.name = name
        self.password = password
        self.misc_data = misc_data

class Contest(db.Model):
    """Stores information about a contest"""
    __tablename__ = 'contest'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    """str: the contest's name"""

    activate_time = db.Column(db.DateTime)
    """DateTime: the contest's activation time, users will be able to see the contest,
        but they will not be able to see the problems or upload submissions"""

    start_time = db.Column(db.DateTime, nullable=False)
    """DateTime: the contest's start time, users will be able to upload submissions at this time"""

    freeze_time = db.Column(db.DateTime)
    """DateTime: the time when the contest's scoreboard freezes"""

    end_time = db.Column(db.DateTime, nullable=False)
    """DateTime: the time when the contest ends, users will not be able to upload submissions
        after this time"""

    deactivate_time = db.Column(db.DateTime)
    """DateTime: the contest will be hidden at this time"""

    is_public = db.Column(db.Boolean, nullable=False)
    """bool: whether or not the contest can be joined/viewed by anyone"""

    def __init__(self, name, start_time, end_time, is_public, activate_time=None, freeze_time=None, deactivate_time=None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.is_public = is_public
        self.activate_time = activate_time
        self.freeze_time = freeze_time
        self.deactivate_time = deactivate_time


class Configuration(db.Model):
    """Stores general configuration information"""
    __tablename__ = 'configuration'

    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(db.String, unique=True, nullable=False)
    """str: the config entry name"""

    val = db.Column(db.String, nullable=False)
    """str: the config entry val"""

    valType = db.Column(db.String, nullable=False)
    """str: the type of the config entry val"""

    def __init__(self, key, val, valType):
        self.key = key
        self.val = val
        self.valType = valType
