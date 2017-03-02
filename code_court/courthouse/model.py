import json
import datetime

import util

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

contest_problem = db.Table('contest_problem', db.Model.metadata,
    db.Column('contest_id', db.Integer, db.ForeignKey('contest.id')),
    db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
)

contest_user = db.Table('contest_user', db.Model.metadata,
    db.Column('contest_id', db.Integer, db.ForeignKey('contest.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

user_user_role = db.Table('user_user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('user_role_id', db.Integer, db.ForeignKey('user_role.id'))
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

    def get_output_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_enabled": self.is_enabled,
            "run_script": self.run_script
        }

    def __str__(self):
        return "Language({})".format(self.name)

    def __repr__(self):
        return "Language({})".format(self.name)

    def __str__(self):
        return self.__repr__()


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

    def get_output_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "eval_script": self.eval_script,
        }

    def __repr__(self):
        return "ProblemType({})".format(self.name)

    def __str__(self):
        return self.__repr__()


class Problem(db.Model):
    __tablename__ = 'problem'

    id = db.Column(db.Integer, primary_key=True)

    problem_type = db.relationship('ProblemType', backref=db.backref('Problem', lazy='dynamic'))
    problem_type_id = db.Column(db.Integer, db.ForeignKey('problem_type.id'), nullable=False)
    """int: a foreignkey to the problem's problem type"""

    slug = db.Column(db.String(10), unique=True, nullable=False)
    """str: the problem's slug, this is a short (<11 chars) string that is used to identify
            a problem. It can only contain the following characters: a-z, A-Z, 0-1, -, _"""

    name = db.Column(db.String, nullable=False)
    """str: the problem's name"""

    problem_statement = db.Column(db.String, nullable=False)
    """str: the problem statement in markdown format"""

    sample_input = db.Column(db.String, nullable=False)
    """str: the problem's sample input, this may be shown to the user """

    sample_output = db.Column(db.String, nullable=False)
    """str: the problem's sample output, this may be shown to the user """

    secret_input = db.Column(db.String, nullable=False)
    """str: the problem's secret input, this may be shown to the user """

    secret_output = db.Column(db.String, nullable=False)
    """str: the problem's secret output, this may be shown to the user """

    contests = db.relationship("Contest", secondary=contest_problem, back_populates="problems")

    def __init__(self, problem_type, slug, name, problem_statement, sample_input,
                 sample_output, secret_input, secret_output):
        self.problem_type = problem_type
        self.slug = slug
        self.name = name
        self.problem_statement = problem_statement
        self.sample_input = sample_input
        self.sample_output = sample_output
        self.secret_input = secret_input
        self.secret_output = secret_output

    def get_output_dict(self):
        return {
            "id": self.id,
            "problem_type": self.problem_type.get_output_dict(),
            "slug": self.slug,
            "name": self.name,
            "problem_statement": self.problem_statement,
            "sample_input": self.sample_input,
            "sample_output": self.sample_output,
        }

    def __repr__(self):
        return "Problem({})".format(self.name)

    def __str__(self):
        return self.__repr__()

class User(db.Model, UserMixin):
    """Stores information about a user"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String, unique=True, nullable=False)
    """str: the user's email"""

    name = db.Column(db.String, nullable=False)
    """str: the user's full name, no specific format is assumed"""

    hashed_password = db.Column(db.String, nullable=False)
    """str: a bcrypt hash of the user's password"""

    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    """str: the creation time of the user"""

    misc_data = db.Column(db.String, nullable=False)
    """str: misc data about a user, stored as a json object"""

    contests = db.relationship("Contest", secondary=contest_user, back_populates="users")
    user_roles = db.relationship("UserRole", secondary=user_user_role, back_populates="users")

    def __init__(self, email, name, password, creation_time=None, misc_data=None, user_roles=None):
        if misc_data is None:
            misc_data = json.dumps({})

        if creation_time is None:
            self.creation_time = datetime.datetime.utcnow()

        if user_roles is not None:
            self.user_roles = user_roles

        self.email = email
        self.name = name
        self.hashed_password = util.hash_password(password)
        self.misc_data = misc_data

    def verify_password(self, plainext_password):
        return util.is_password_matching(plainext_password, self.hashed_password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def get_output_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
        }

    def __repr__(self):
        return "User({})".format(self.email)

    def __str__(self):
        return self.__repr__()


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

    # users = db.relationship("ContestUser", back_populates="contest")
    users = db.relationship("User", secondary=contest_user, back_populates="contests")
    problems = db.relationship("Problem", secondary=contest_problem, back_populates="contests")

    def __init__(self, name, start_time, end_time, is_public, activate_time=None, freeze_time=None, deactivate_time=None, users=None, problems=None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.is_public = is_public
        self.activate_time = activate_time
        self.freeze_time = freeze_time
        self.deactivate_time = deactivate_time
        self.users = users or []
        self.problems = problems or []

    def get_output_dict(self):
        return {
            "id": self.id
        }

    def __repr__(self):
        return "Contest({})".format(self.name)

    def __str__(self):
        return self.__repr__()



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

    def get_output_dict(self):
        return {
            "id": self.id
        }

    def __repr__(self):
        return "Configuration({}={})".format(self.key, self.val)

    def __str__(self):
        return self.__repr__()


class SavedCode(db.Model):
    """Stores general configuration information"""
    __tablename__ = 'saved_code'

    id = db.Column(db.Integer, primary_key=True)

    contest = db.relationship('Contest', backref=db.backref('SavedCode', lazy='dynamic'))
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), nullable=False)
    """int: a foreignkey to the saved_code's contest"""

    problem = db.relationship('Problem', backref=db.backref('SavedCode', lazy='dynamic'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    """int: a foreignkey to the saved_code's problem"""

    user = db.relationship('User', backref=db.backref('SavedCode', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    """int: a foreignkey to the saved_code's user"""

    language = db.relationship('Language', backref=db.backref('SavedCode', lazy='dynamic'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    """int: a foreignkey to the saved_code's language"""

    source_code = db.Column(db.String, unique=True, nullable=False)
    """str: the saved source code"""

    last_updated_time = db.Column(db.DateTime)
    """DateTime: the time the code was last updated at"""

    def __init__(self, contest, problem, user, language, source_code, last_updated_time):
        self.contest = contest
        self.problem = problem
        self.user = user
        self.language = language
        self.source_code = source_code
        self.last_updated_time = last_updated_time

    def get_output_dict(self):
        return {
            "id": self.id
        }

    def __repr__(self):
        return "SavedCode(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()


class Run(db.Model):
    """Stores information about a specific run. This might be a
    submission, or just a test run"""
    __tablename__ = 'run'
    id = db.Column(db.Integer, primary_key=True)

    user = db.relationship('User', backref=db.backref('Run', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    """int: a foreignkey to the run's user"""

    contest = db.relationship('Contest', backref=db.backref('Run', lazy='dynamic'))
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), nullable=False)
    """int: a foreignkey to the run's contest"""

    language = db.relationship('Language', backref=db.backref('Run', lazy='dynamic'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    """int: a foreignkey to the run's language"""

    problem = db.relationship('Problem', backref=db.backref('Run', lazy='dynamic'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    """int: a foreignkey to the run's problem"""

    source_code = db.Column(db.String, nullable=False)
    """str: the submitted source code"""

    submit_time = db.Column(db.DateTime, nullable=False)
    """DateTime: the time the code was submitted"""

    started_execing_time = db.Column(db.DateTime)
    """DateTime: the time the code started being executed"""

    finished_execing_time = db.Column(db.DateTime)
    """DateTime: the time the code finished being executed"""

    run_input = db.Column(db.String, nullable=False)
    """str: input text passed to the submitted program"""

    correct_output = db.Column(db.String)
    """str: the correct output of the submitted program"""

    run_output = db.Column(db.String)
    """str: the output of the submitted program"""

    is_submission = db.Column(db.Boolean, nullable=False)
    """bool: if true the run is a submission, if false it's a test run"""

    is_passed = db.Column(db.Boolean, nullable=True)
    """bool: indicates whether or not a run has been judged as passing or failing"""

    @property
    def is_judging(self):
        return (self.started_execing_time is not None and
                self.finished_execing_time is None)

    @property
    def is_judged(self):
        return self.finished_execing_time is not None

    def __init__(self, user, contest, language, problem, submit_time, source_code, run_input, correct_output, is_submission):
        self.user = user
        self.contest = contest
        self.language = language
        self.problem = problem
        self.submit_time = submit_time
        self.source_code =  source_code
        self.run_input = run_input
        self.correct_output = correct_output
        self.is_submission = is_submission

    def get_output_dict(self):
        return {
            "id": self.id
        }

    def __repr__(self):
        return "Run(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def get_judging_runs():
        return Run.query.filter(Run.started_execing_time != None).\
                         filter(Run.finished_execing_time == None).all()

    @staticmethod
    def get_unjudged_runs():
        return Run.query.filter(Run.finished_execing_time == None).all()


class Clarification(db.Model):
    """Stores information about a user or judge clarification"""
    __tablename__ = 'clarification'

    id = db.Column(db.Integer, primary_key=True)

    contest = db.relationship('Contest', backref=db.backref('Clarification', lazy='dynamic'))
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), nullable=False)
    """int: a foreignkey to the clarification's contest"""

    problem = db.relationship('Problem', backref=db.backref('Clarification', lazy='dynamic'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=True)
    """int: a foreignkey to the clarification's problem, if it is null, the
        the clarification is general"""

    asker_user = db.relationship('User', backref=db.backref('Clarification', lazy='dynamic'))
    asker_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    """int: a foreignkey to the user that initiated the clarification"""

    parent = db.relationship("Clarification", remote_side=[id])
    parent_id = db.Column(db.Integer, db.ForeignKey('clarification.id'), nullable=True)
    """int: a foreignkey to the a parent clarification"""

    contents = db.Column(db.String, nullable=False)
    """str: the contents of the clarification"""

    creation_time = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)
    """DateTime: the time the clarification was created at"""

    is_public = db.Column(db.Boolean, nullable=False)
    """bool: whether or not the clarification is shown to everyone, or just the intiator"""

    def get_output_dict(self):
        return {
            "id": self.id
        }

    def __repr__(self):
        return "Clarification(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()


class UserRole(db.Model):
    """Stores system user roles"""
    __tablename__ = 'user_role'

    id = db.Column(db.String, primary_key=True)

    users = db.relationship("User", secondary=user_user_role, back_populates="user_roles")

    def __init__(self, name):
        self.id = name

    def get_output_dict(self):
        return {
            "id": self.id
        }

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.id == other.id
        elif isinstance(other, str):
            return self.id == other
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "UserRole(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()

def str_to_dt(s):
    """Converts a string in format 2017-12-30T12:60 to datetime"""
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M')

def dt_to_str(dt):
    """Converts a datetime to a string in format 2017-12-30T12:60"""
    return datetime.datetime.strftime(dt, '%Y-%m-%dT%H:%M')
