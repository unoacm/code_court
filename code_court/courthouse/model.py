import json
import datetime

import util

from flask_login import UserMixin
from database import Base

from sqlalchemy.orm import relationship, backref

from sqlalchemy import (
    Column,
    Table,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
)

MAX_RUN_OUTPUT_LENGTH = 2000

contest_problem = Table('contest_problem', Base.metadata,
                           Column('contest_id', Integer,
                                     ForeignKey('contest.id')),
                           Column('problem_id', Integer,
                                     ForeignKey('problem.id')))

contest_user = Table('contest_user', Base.metadata,
                        Column('contest_id', Integer,
                                  ForeignKey('contest.id')),
                        Column('user_id', Integer,
                                  ForeignKey('user.id')))

user_user_role = Table('user_user_role', Base.metadata,
                          Column('user_id', Integer,
                                    ForeignKey('user.id')),
                          Column('user_role_id', Integer,
                                    ForeignKey('user_role.id')))


class Language(Base):
    """Stores the configuration for a programming language"""
    __tablename__ = 'language'

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False)
    """str: the language name"""

    default_template = Column(String)
    """str: the languages default template"""

    syntax_mode = Column(String, nullable=False)
    """str: the syntax mode used by the code editor"""

    is_enabled = Column(Boolean, nullable=False)
    """bool: whether or not the language is enabled"""

    run_script = Column(String, nullable=False)
    """str: script (with shebang) that compiles and runs scripts for this language"""

    def __init__(self,
                 name,
                 syntax_mode,
                 is_enabled,
                 run_script,
                 default_template=None):
        self.name = name
        self.syntax_mode = syntax_mode
        self.is_enabled = is_enabled
        self.run_script = run_script
        self.default_template = default_template

    def get_output_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_enabled": self.is_enabled,
            "run_script": self.run_script,
            "default_template": self.default_template
        }

    def __str__(self):
        return "Language({})".format(self.name)

    def __repr__(self):
        return "Language({})".format(self.name)


class ProblemType(Base):
    """Stores information about a problem type"""
    __tablename__ = 'problem_type'

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, nullable=False)
    """str: the name of the problem type"""

    eval_script = Column(String, nullable=False)
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


class Problem(Base):
    __tablename__ = 'problem'

    id = Column(Integer, primary_key=True)

    problem_type = relationship(
        'ProblemType', backref=backref('Problem', lazy='dynamic'))
    problem_type_id = Column(
        Integer, ForeignKey('problem_type.id'), nullable=False)
    """int: a foreignkey to the problem's problem type"""

    slug = Column(String(200), unique=True, nullable=False)
    """str: the problem's slug, this is a short (<11 chars) string that is used to identify
            a problem. It can only contain the following characters: a-z, A-Z, 0-1, -, _"""

    name = Column(String, nullable=False)
    """str: the problem's name"""

    problem_statement = Column(String, nullable=False)
    """str: the problem statement in markdown format"""

    sample_input = Column(String, nullable=False)
    """str: the problem's sample input, this may be shown to the user """

    sample_output = Column(String, nullable=False)
    """str: the problem's sample output, this may be shown to the user """

    secret_input = Column(String, nullable=False)
    """str: the problem's secret input, this may be shown to the user """

    secret_output = Column(String, nullable=False)
    """str: the problem's secret output, this may be shown to the user """

    is_enabled = Column(Boolean, nullable=False, default=True)
    """bool: whether or not the problem is enabled"""

    contests = relationship(
        "Contest", secondary=contest_problem, back_populates="problems")

    def __init__(self, problem_type, slug, name, problem_statement,
                 sample_input, sample_output, secret_input, secret_output):
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


class User(Base, UserMixin):
    """Stores information about a user"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)

    email = Column(String, unique=True, nullable=False)
    """str: the user's email"""

    name = Column(String, nullable=False)
    """str: the user's full name, no specific format is assumed"""

    username = Column(String, nullable=False)
    """str: the username, for display"""

    hashed_password = Column(String, nullable=False)
    """str: a bcrypt hash of the user's password"""

    creation_time = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow())
    """str: the creation time of the user"""

    misc_data = Column(String, nullable=False)
    """str: misc data about a user, stored as a json object"""

    contests = relationship(
        "Contest", secondary=contest_user, back_populates="users")
    user_roles = relationship(
        "UserRole", secondary=user_user_role, back_populates="users")

    def __init__(self,
                 email,
                 name,
                 password,
                 creation_time=None,
                 misc_data=None,
                 contests=None,
                 user_roles=None,
                 username=None):
        if misc_data is None:
            misc_data = json.dumps({})

        if creation_time is None:
            self.creation_time = datetime.datetime.utcnow()

        if user_roles is not None:
            self.user_roles = user_roles

        if contests is not None:
            self.contests = contests

        self.email = email
        self.name = name
        self.hashed_password = str(util.hash_password(password))
        self.misc_data = misc_data
        if username:
            self.username = username
        else:
            self.username = email.split("@")[0]

    @property
    def misc_data_dict(self):
        return json.loads(self.misc_data)

    def verify_password(self, plainext_password):
        return util.is_password_matching(plainext_password,
                                         self.hashed_password)

    def merge_metadata(self, new_metadata_dict):
        old_metadata_dict = json.loads(self.misc_data)

        old_metadata_dict.update(new_metadata_dict)

        self.misc_data = json.dumps(old_metadata_dict)

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
            "username": self.username,
        }

    def __repr__(self):
        return "User({})".format(self.email)

    def __str__(self):
        return self.__repr__()


class Contest(Base):
    """Stores information about a contest"""
    __tablename__ = 'contest'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    """str: the contest's name"""

    activate_time = Column(DateTime)
    """DateTime: the contest's activation time, users will be able to see the contest,
        but they will not be able to see the problems or upload submissions"""

    start_time = Column(DateTime, nullable=False)
    """DateTime: the contest's start time, users will be able to upload submissions at this time"""

    freeze_time = Column(DateTime)
    """DateTime: the time when the contest's scoreboard freezes"""

    end_time = Column(DateTime, nullable=False)
    """DateTime: the time when the contest ends, users will not be able to upload submissions
        after this time"""

    deactivate_time = Column(DateTime)
    """DateTime: the contest will be hidden at this time"""

    is_public = Column(Boolean, nullable=False)
    """bool: whether or not the contest can be joined/viewed by anyone"""

    # users = relationship("ContestUser", back_populates="contest")
    users = relationship(
        "User", secondary=contest_user, back_populates="contests")
    problems = relationship(
        "Problem", secondary=contest_problem, back_populates="contests")

    def __init__(self,
                 name,
                 start_time,
                 end_time,
                 is_public,
                 activate_time=None,
                 freeze_time=None,
                 deactivate_time=None,
                 users=None,
                 problems=None):
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
            "id": self.id,
            "name": self.name,
            "is_public": self.is_public,
            "activate_time": dt_to_str(self.activate_time),
            "start_time": dt_to_str(self.start_time),
            "freeze_time": dt_to_str(self.freeze_time),
            "end_time": dt_to_str(self.end_time),
            "deactivate_time": dt_to_str(self.deactivate_time),
        }

    def __repr__(self):
        return "Contest({})".format(self.name)

    def __str__(self):
        return self.__repr__()


class Configuration(Base):
    """Stores general configuration information"""
    __tablename__ = 'configuration'

    id = Column(Integer, primary_key=True)

    key = Column(String, unique=True, nullable=False)
    """str: the config entry name"""

    val = Column(String, nullable=False)
    """str: the config entry val"""

    valType = Column(String, nullable=False)
    """str: the type of the config entry val"""

    category = Column(String, nullable=False)
    """str: the config entry category """

    def __init__(self, key, val, valType, category):
        self.key = key
        self.val = val
        self.valType = valType
        self.category = category

    def get_output_dict(self):
        return {"id": self.id}

    def __repr__(self):
        return "Configuration({}={})".format(self.key, self.val)

    def __str__(self):
        return self.__repr__()


class SavedCode(Base):
    """Stores general configuration information"""
    __tablename__ = 'saved_code'

    id = Column(Integer, primary_key=True)

    contest = relationship(
        'Contest', backref=backref('SavedCode', lazy='dynamic'))
    contest_id = Column(
        Integer, ForeignKey('contest.id'), nullable=False)
    """int: a foreignkey to the saved_code's contest"""

    problem = relationship(
        'Problem', backref=backref('SavedCode', lazy='dynamic'))
    problem_id = Column(
        Integer, ForeignKey('problem.id'), nullable=False)
    """int: a foreignkey to the saved_code's problem"""

    user = relationship(
        'User', backref=backref('SavedCode', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    """int: a foreignkey to the saved_code's user"""

    language = relationship(
        'Language', backref=backref('SavedCode', lazy='dynamic'))
    language_id = Column(
        Integer, ForeignKey('language.id'), nullable=False)
    """int: a foreignkey to the saved_code's language"""

    source_code = Column(String, unique=True, nullable=False)
    """str: the saved source code"""

    last_updated_time = Column(DateTime)
    """DateTime: the time the code was last updated at"""

    def __init__(self, contest, problem, user, language, source_code,
                 last_updated_time):
        self.contest = contest
        self.problem = problem
        self.user = user
        self.language = language
        self.source_code = source_code
        self.last_updated_time = last_updated_time

    def get_output_dict(self):
        return {"id": self.id}

    def __repr__(self):
        return "SavedCode(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()


class Run(Base):
    """Stores information about a specific run. This might be a
    submission, or just a test run"""
    __tablename__ = 'run'
    id = Column(Integer, primary_key=True)

    user = relationship('User', backref=backref('Run', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    """int: a foreignkey to the run's user"""

    contest = relationship(
        'Contest', backref=backref('Run', lazy='dynamic'))
    contest_id = Column(
        Integer, ForeignKey('contest.id'), nullable=False)
    """int: a foreignkey to the run's contest"""

    language = relationship(
        'Language', backref=backref('Run', lazy='dynamic'))
    language_id = Column(
        Integer, ForeignKey('language.id'), nullable=False)
    """int: a foreignkey to the run's language"""

    problem = relationship(
        'Problem', backref=backref('Run', lazy='dynamic'))
    problem_id = Column(
        Integer, ForeignKey('problem.id'), nullable=False)
    """int: a foreignkey to the run's problem"""

    source_code = Column(String, nullable=False)
    """str: the submitted source code"""

    submit_time = Column(DateTime, nullable=False)
    """DateTime: the time the code was submitted"""

    local_submit_time = Column(DateTime, nullable=True)
    """DateTime: the time the code was submitted"""

    started_execing_time = Column(DateTime)
    """DateTime: the time the code started being executed"""

    finished_execing_time = Column(DateTime)
    """DateTime: the time the code finished being executed"""

    run_input = Column(String, nullable=False)
    """str: input text passed to the submitted program"""

    correct_output = Column(String)
    """str: the correct output of the submitted program"""

    run_output = Column(String)
    """str: the output of the submitted program"""

    is_submission = Column(Boolean, nullable=False)
    """bool: if true the run is a submission, if false it's a test run"""

    is_passed = Column(Boolean, nullable=True)
    """bool: indicates whether or not a run has been judged as passing or failing"""

    is_priority = Column(Boolean, default=False)
    """bool: indicates whether or not a run has priority status, which expedites execution"""

    state = Column(String)
    """str: information about the execution of the program"""

    @property
    def is_judging(self):
        return (self.started_execing_time is not None
                and self.finished_execing_time is None)

    @property
    def is_judged(self):
        return self.finished_execing_time is not None

    def __init__(self, user, contest, language, problem, submit_time,
                 source_code, run_input, correct_output, is_submission, local_submit_time =None):
        self.user = user
        self.contest = contest
        self.language = language
        self.problem = problem
        self.submit_time = submit_time
        self.source_code = source_code
        self.run_input = run_input
        self.correct_output = correct_output
        self.is_submission = is_submission
        if local_submit_time:
            self.local_submit_time = local_submit_time

    def get_output_dict(self):
        d = {
            "id": self.id,
            "source_code": self.source_code,
            "language": self.language.name,
            "submit_time": self.submit_time,
            "started_execing_time": self.started_execing_time,
            "finished_execing_time": self.finished_execing_time,
            "is_submission": self.is_submission,
            "is_passed": self.is_passed,
            "is_priority": self.is_priority,
            "state": self.state
        }

        if self.local_submit_time:
            d["local_submit_time"] = self.local_submit_time

        if not self.is_submission:
            d["run_input"] = self.run_input
            d["correct_output"] = self.correct_output

            run_output = self.run_output
            if run_output and len(run_output) > MAX_RUN_OUTPUT_LENGTH:
                run_output = run_output[0:MAX_RUN_OUTPUT_LENGTH]
                run_output += "\n...[truncated]..."

            d["run_output"] = run_output

        return d

    def __repr__(self):
        return "Run(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def get_judging_runs():
        return Run.query.filter(Run.started_execing_time is not None).\
                         filter(Run.finished_execing_time is None).all()

    @staticmethod
    def get_unjudged_runs():
        return Run.query.filter(Run.finished_execing_time is None).all()


class Clarification(Base):
    """Stores information about a user or judge clarification"""
    __tablename__ = 'clarification'

    id = Column(Integer, primary_key=True)

    problem = relationship(
        'Problem', backref=backref('Clarification', lazy='dynamic'))
    problem_id = Column(
        Integer, ForeignKey('problem.id'), nullable=True)
    """int: a foreignkey to the clarification's problem, if it is null, the
        the clarification is general"""

    initiating_user = relationship(
        'User', backref=backref('Clarification', lazy='dynamic'))
    initiating_user_id = Column(
        Integer, ForeignKey('user.id'), nullable=False)
    """int: a foreignkey to the user that initiated the clarification"""

    parent = relationship("Clarification", remote_side=[id])
    parent_id = Column(
        Integer, ForeignKey('clarification.id'), nullable=True)
    """int: a foreignkey to the a parent clarification"""

    thread = Column(String, nullable=False)
    """str: this is a uuid that indicates which thread this clarification belongs to"""

    subject = Column(String, nullable=False)
    """str: the title of the clairification, gives brief idea of contents"""

    contents = Column(String, nullable=False)
    """str: the contents of the clarification"""

    creation_time = Column(
        DateTime, default=datetime.datetime.utcnow(), nullable=False)
    """DateTime: the time the clarification was created at"""

    is_public = Column(Boolean, nullable=False)
    """bool: whether or not the clarification is shown to everyone, or just the intiator"""

    def __init__(self, initiating_user, subject, contents, thread, is_public):
        self.initiating_user = initiating_user
        self.subject = subject
        self.contents = contents
        self.thread = thread
        self.is_public = is_public

    def get_output_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "contents": self.contents,
            "thread": self.contents,
            "is_public": self.is_public,
            "initiating_user": self.initiating_user
        }

    def __repr__(self):
        return "Clarification(id={})".format(self.id)

    def __str__(self):
        return self.__repr__()


class UserRole(Base):
    """Stores system user roles"""
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    users = relationship(
        "User", secondary=user_user_role, back_populates="user_roles")

    def __init__(self, name):
        self.name = name

    def get_output_dict(self):
        return {"name": self.name}

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "UserRole(name={})".format(self.name)

    def __str__(self):
        return self.__repr__()


def str_to_dt(s):
    """Converts a string in format 2017-12-30T12:60Z to datetime"""
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%MZ')


def strs_to_dt(date_string, time_string):
    """Converts two strings in formats "2017-12-30" and "12:60" to datetime"""
    return str_to_dt(date_string + "T" + time_string + "Z")


def time_str_to_dt(s):
    """Converts a string in format 12:59 to datetime"""
    return datetime.datetime.strptime(s, '%H:%M')


def dt_to_str(dt):
    """Converts a datetime to a string in format 2017-12-30T12:60Z"""
    if dt is None:
        return None
    return datetime.datetime.strftime(dt, '%Y-%m-%dT%H:%MZ')


def dt_to_date_str(dt):
    """Converts a datetime to a string in format 2017-12-30"""
    if dt is None:
        return None
    return datetime.datetime.strftime(dt, '%Y-%m-%d')


def dt_to_time_str(dt):
    """Converts a datetime to a string in format 12:59"""
    if dt is None:
        return None
    return datetime.datetime.strftime(dt, '%H:%M')

