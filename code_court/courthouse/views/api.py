"""
Contains api endpoints for the defendant frontend
and external services
"""
import datetime
import itertools
import time
import uuid

import util

from flask_httpauth import HTTPBasicAuth
from flask_login import current_user
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

import six

from sqlalchemy.orm import joinedload

from flask import (
    abort,
    Blueprint,
    current_app,
    jsonify,
    make_response,
    request,
    url_for, )

from database import db_session
import model

api = Blueprint('api', __name__, template_folder='templates')
executioner_auth = HTTPBasicAuth()


# api auth
@executioner_auth.verify_password
def verify_password(email, password):
    user = model.User.query.filter_by(email=email).scalar()
    if not user or not user.verify_password(password):
        return False
    return True


@executioner_auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


# api routes
@api.route("/get-writ", methods=["GET"])
@executioner_auth.login_required
def get_writ():
    """endpoint for executioners to get runs to execute"""

    # choose oldest priority run
    chosen_run = model.Run.query.filter_by(is_priority=True, started_execing_time=None, finished_execing_time=None)\
                                .order_by(model.Run.submit_time.asc()).limit(1).first()

    # if no priority runs, choose oldest non-priority run
    if chosen_run is None:
        chosen_run = model.Run.query.filter_by(started_execing_time=None, finished_execing_time=None)\
                                    .order_by(model.Run.submit_time.asc()).limit(1).first()
    if chosen_run is None:
        return make_response(jsonify({'status': 'unavailable'}), 404)

    # TODO: use a better locking method to prevent dual execution
    chosen_run.started_execing_time = datetime.datetime.utcnow()
    db_session.commit()

    resp = {
        "status": "found",
        "source_code": chosen_run.source_code,
        "language": chosen_run.language.name,
        "run_script": chosen_run.language.run_script,
        "input": chosen_run.run_input,
        "run_id": chosen_run.id,
        "return_url": url_for("api.submit_writ", run_id=chosen_run.id, _external=True)
    }

    return make_response(jsonify(resp), 200)


@api.route("/submit-writ/<run_id>", methods=["POST"])
@executioner_auth.login_required
def submit_writ(run_id):
    """endpoint for executioners to submit runs

    Looking for the format:
    {
        "output": "..."
    }
    """
    run = model.Run.query.get(util.i(run_id))

    if not run:
        current_app.logger.debug("Received writ without valid run, id: %s",
                                 run_id)
        abort(404)

    if run.finished_execing_time:
        current_app.logger.warning(
            "Received writ submission for already submitted run, id: %s",
            run_id)
        abort(400)

    if not request.json:
        current_app.logger.debug("Received writ without json")
        abort(400)

    if 'output' not in request.json or not isinstance(request.json['output'],
                                                      six.string_types):
        current_app.logger.debug("Received writ without the output field")
        abort(400)

    run.run_output = request.json.get('output')
    run.state = request.json.get('state') or run.state
    run.finished_execing_time = datetime.datetime.utcnow()

    if run.is_submission:
        run.is_passed = clean_output_string(
            run.run_output) == clean_output_string(run.correct_output)

        if run.is_passed:
            util.invalidate_cache_item(util.SCORE_CACHE_NAME, run.contest.id)

        if run.state == model.RunState.EXECUTED:
            if run.is_passed:
                run.state = model.RunState.SUCCESSFUL
            else:
                run.state = model.RunState.FAILED

    db_session.commit()

    util.invalidate_cache_item(util.RUN_CACHE_NAME, run.user_id)
    return "Good"


@api.route("/return-without-run/<run_id>", methods=["POST"])
@executioner_auth.login_required
def return_without_run(run_id):
    """Allows for executors to return a writ without running if they are
    experiencing errors or are shutting down
    """
    run = model.Run.query.get(util.i(run_id))
    if not run:
        current_app.logger.debug("Received writ without valid run, id: %s",
                                 run_id)
        abort(404)

    if run.finished_execing_time:
        current_app.logger.warning(
            "Received return for already returned writ, id: %s", run_id)
        abort(400)

    run.started_execing_time = None
    db_session.commit()

    return "Good"


@api.route('/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify({"msg": "Bad request"}), 401

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    user = model.User.query.filter_by(email=email).scalar()

    if user and user.verify_password(password):
        ret = {'access_token': create_access_token(identity=user.id)}
        return jsonify(ret), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@api.route("/problem/<slug>", methods=["GET"])
def get_problem(slug):
    problem = model.Problem.query.filter_by(slug=slug).scalar()

    return make_response(jsonify(problem.get_output_dict()), 200)


@api.route("/problems/<user_id>")
@api.route("/problems")
@jwt_required
def get_all_problems(user_id=None):
    current_user_id = get_jwt_identity()
    curr_user = model.User.query.get(util.i(current_user_id))

    problems = model.Problem.query.filter_by(is_enabled=True).all()
    runs = model.Run.query.filter_by(user=curr_user).all()

    if len(curr_user.contests) == 0:
        return make_response(
            jsonify({
                'error': 'User has no contests'
            }), 400)

    problems = (p for p in problems if curr_user.contests[0] in p.contests)

    resp = {}
    for problem in problems:
        problem_run_dicts = [x.get_output_dict() for x in runs if x.problem == problem]

        problem_dict = problem.get_output_dict()
        problem_dict['runs'] = problem_run_dicts

        resp[problem.slug] = problem_dict

    return make_response(jsonify(resp), 200)


@api.route("/submit_clarification", methods=["POST"])
@jwt_required
def submit_clarification():
    subject = request.json.get('subject', None)
    contents = request.json.get('contents', None)
    problem_slug = request.json.get('problem_slug', None)
    parent_id = request.json.get('parent_id', None)

    problem = model.Problem.query.filter_by(slug=problem_slug).scalar()

    thread = ""
    if parent_id is None:
        thread = str(uuid.uuid4())
    else:
        thread = model.Clarification.query.filter_by(
            id=parent_id).scalar().thread

    is_public = False  # user submitted clarifications are always false
    clar = model.Clarification(current_user, subject, contents, thread,
                               is_public)
    clar.problem = problem

    db_session.add(clar)
    db_session.commit()

    return "{}"


@api.route("/languages", methods=["GET"])
def get_languages():
    langs = model.Language.query.all()
    filter_langs = [x.get_output_dict() for x in langs if x.is_enabled]

    return make_response(jsonify(filter_langs), 200)


@api.route("/current-user", methods=["GET"])
@jwt_required
def get_current_user():
    current_user_id = get_jwt_identity()
    curr_user = model.User.query.get(util.i(current_user_id))

    resp = None
    if curr_user:
        resp = curr_user.get_output_dict()

    return make_response(jsonify(resp), 200)


@api.route("/submit-run", methods=["POST"])
@jwt_required
def submit_run():
    current_user_id = get_jwt_identity()
    user = model.User.query.get(util.i(current_user_id))

    MAX_RUNS = util.get_configuration("max_user_submissions")
    TIME_LIMIT = util.get_configuration("user_submission_time_limit")

    over_limit_runs_query = model.Run.submit_time >\
                            (datetime.datetime.utcnow() - datetime.timedelta(minutes=TIME_LIMIT))
    run_count = model.Run.query.filter_by(user_id=user.id)\
                               .filter(over_limit_runs_query)\
                               .count()

    if run_count > MAX_RUNS:
        return make_response(
            jsonify({
                'error': 'Submission rate limit exceeded'
            }), 400)


    contest = user.contests[0]

    lang_name = request.json.get('lang', None)
    problem_slug = request.json.get('problem_slug', None)
    source_code = request.json.get('source_code', None)
    is_submission = request.json.get('is_submission', False)
    user_test_input = request.json.get('user_test_input', None)

    if not all([lang_name, problem_slug, source_code]):
        return make_response(
            jsonify({
                'error': 'Invalid submission, missing input'
            }), 400)

    lang = model.Language.query.filter_by(name=lang_name).scalar()
    if not lang:
        return make_response(
            jsonify({
                'error': 'Invalid language'
            }), 400)

    problem = model.Problem.query.filter_by(slug=problem_slug).scalar()
    if not problem:
        return make_response(
            jsonify({
                'error': 'Invalid problem slug'
            }), 400)


    run_input = None
    correct_output = None
    if is_submission:
        run_input = problem.secret_input
        correct_output = problem.secret_output
    else:
        if user_test_input:
            run_input = user_test_input
        else:
            run_input = problem.sample_input
        correct_output = problem.sample_output

    run = model.Run(user, contest, lang, problem,
                    datetime.datetime.utcnow(), source_code, run_input,
                    correct_output, is_submission, local_submit_time=datetime.datetime.now())
    run.state = model.RunState.JUDGING

    resp = None
    if datetime.datetime.utcnow() > contest.end_time:
        run.state = model.RunState.CONTEST_ENDED
        resp = make_response(jsonify({'error': 'Contest has ended'}), 400)
    elif datetime.datetime.utcnow() < contest.start_time:
        run.state = model.RunState.CONTEST_HAS_NOT_BEGUN
        run.started_execing_time = datetime.datetime.utcnow()
        run.finished_execing_time = datetime.datetime.utcnow()
        resp = make_response(jsonify({'error': 'Contest has not begun'}), 400)
    else:
        resp = make_response(jsonify({'status': 'good'}), 200)

    db_session.add(run)
    db_session.commit()

    util.invalidate_cache_item(util.RUN_CACHE_NAME, run.user_id)

    return resp


@api.route("/scores/<contest_id>", methods=["GET"])
def get_scoreboard(contest_id):
    contest = model.Contest.query.get(contest_id)

    if not contest:
        return make_response(jsonify({'error': 'Could not find contest'}), 404)

    defendants = model.User.query\
                      .filter(model.User.user_roles.any(name="defendant"))\
                      .filter(model.User.contests.any(id=contest.id))\
                      .all()

    problems = model.Problem.query\
                    .filter(model.Problem.contests.any(id=contest.id))\
                    .filter(model.Problem.is_enabled)\
                    .all()

    runs = model.Run.query.filter_by(
            is_submission=True,
            contest=contest).options(joinedload(model.Run.user), joinedload(model.Run.problem)).all()
    key = lambda x: (x.user.id, x.problem.id, x.is_passed)

    runs = {k: list(v) for k, v in itertools.groupby(sorted(filter(lambda x: x.user.id is not None and x.problem.id is not None and x.is_passed is not None, runs), key=key), key=key)}

    user_points = []
    for user in defendants:
        problem_states = {}
        penalty = 0
        for problem in problems:
            problem_states[problem.slug] = len(runs.get((user.id, problem.id, True), [])) > 0
            penalty += len(runs.get((user.id, problem.id, False), [])) if (user.id, problem.id, True) in runs else 0

        user_points.append({
            "user":
            user.get_output_dict(),
            "num_solved":
            len([x for x in problem_states.values() if x]),
            "penalty":
            penalty,
            "problem_states":
            problem_states
        })

    user_points.sort(
        key=lambda x: (x["num_solved"], -x["penalty"]), reverse=True)

    return make_response(jsonify(user_points))


@api.route("/get-contest-info")
@jwt_required
def get_contest_info():
    current_user_id = get_jwt_identity()
    curr_user = model.User.query.get(util.i(current_user_id))

    if not curr_user:
        return make_response(jsonify({'error': 'Not logged in'}), 400)

    contests = curr_user.contests

    if len(contests) > 1:
        return make_response(
            jsonify({
                'error': 'User has multiple contests'
            }), 500)

    if len(contests) < 1:
        return make_response(jsonify({'error': 'User has no contests'}), 400)

    contest = contests[0]

    return make_response(jsonify(contest.get_output_dict()))


@api.route("/make-defendant-user", methods=["POST"])
@jwt_required
def make_user():
    """
    To test manually:
    - get auth token: curl -H "Content-Type: application/json" --data '{"email": "admin@example.org", "password": "pass"}' http://localhost:9191/api/login
    - make request: curl -H "Authorization: Bearer *token_goes_here*" -H "Content-Type: application/json" --data '{"name": "Ben", "email": "ben@bendoan.me", "password": "pass"}' http://localhost:9191/api/make-defendant-user
    """
    current_user_id = get_jwt_identity()
    curr_user = model.User.query.get(util.i(current_user_id))

    if not curr_user:
        return make_response(jsonify({'error': 'Not logged in'}), 400)

    if ("judge" not in curr_user.user_roles
            and "operator" not in curr_user.user_roles):
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    email = request.json.get('email')
    name = request.json.get('name')
    password = request.json.get('password')
    username = request.json.get('username')
    contest_name = request.json.get('contest_name')

    if not all([email, name, password, username, contest_name]):
        return make_response(
            jsonify({
                'error': 'Invalid request, missing fields'
            }), 400)

    existing_user = model.User.query.filter_by(email=email).scalar()
    if existing_user:
        return make_response(
            jsonify({
                'error': 'Invalid request, user already exists'
            }), 400)

    defedant_role = model.UserRole.query.filter_by(name="defendant").scalar()

    new_user = model.User(
        email=email,
        name=name,
        password=password,
        user_roles=[defedant_role],
        username=username)

    db_session.add(new_user)
    db_session.commit()

    contest = model.Contest.query.filter_by(name=contest_name).scalar()

    if not contest:
        return make_response(jsonify({'error': 'Invalid contest name'}), 400)

    new_user.contests.append(contest)

    db_session.commit()

    return make_response(jsonify({'status': 'Success'}), 200)


@api.route("/update-user-metadata", methods=["POST"])
@jwt_required
def update_user_metadata():
    current_user_id = get_jwt_identity()
    curr_user = model.User.query.get(util.i(current_user_id))

    if not curr_user:
        return make_response(jsonify({'error': 'Not logged in'}), 400)

    if ("judge" not in curr_user.user_roles
            and "operator" not in curr_user.user_roles):
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    user_email = request.json.get('user_email')
    user_misc_metadata = request.json.get('misc_metadata')

    if not all([user_email, user_misc_metadata]):
        return make_response(
            jsonify({
                'error': 'Invalid request, missing field'
            }), 400)

    if not isinstance(user_misc_metadata, dict):
        return make_response(
            jsonify({
                'error': 'Invalid request, misc_metadata must be a dict'
            }), 400)

    matching_user = model.User.query.filter_by(email=user_email).scalar()

    if not matching_user:
        return make_response(
            jsonify({
                'error': "Invalid request, Couldn't find user"
            }), 400)

    matching_user.merge_metadata(user_misc_metadata)
    db_session.commit()

    return make_response(jsonify({'status': 'Success'}), 200)


@api.route("/load-test")
def load_test():
    existing_user = model.User.query.filter_by(email="testuser1@example.org").scalar()

    contest = model.Contest.query.first()
    defendants = model.User.query\
                      .filter(model.User.user_roles.any(name="defendant"))\
                      .filter(model.User.contests.any(id=contest.id))\
                      .all()

    problems = model.Problem.query\
                    .filter(model.Problem.contests.any(id=contest.id))\
                    .filter(model.Problem.is_enabled)\
                    .all()

    user_points = []
    for user in defendants:
        problem_states = {}
        penalty = 0
        for problem in problems:
            is_passed = 0 < len(
                model.Run.query.filter_by(
                    is_submission=True,
                    is_passed=True,
                    user=user,
                    contest=contest,
                    problem=problem).all())
            problem_states[problem.slug] = is_passed

            failed_subs = model.Run.query.filter_by(
                is_submission=True,
                is_passed=False,
                user=user,
                contest=contest,
                problem=problem).all()

            for sub in failed_subs:
                penalty += 1  # TODO we may want to use the time submitted instead of 1
                #      to match ICPC scoring

        user_points.append({
            "user":
            user.get_output_dict(),
            "num_solved":
            len([x for x in problem_states.values() if x]),
            "penalty":
            penalty,
            "problem_states":
            problem_states
        })

    user_points.sort(
        key=lambda x: (x["num_solved"], -x["penalty"]), reverse=True)

    user = model.User.query.filter_by(email="testuser1@example.org").scalar()
    if not user or not user.verify_password("test"):
        pass

    user = model.User.query.filter_by(email="notauser@example.org").scalar()
    if not user or not user.verify_password("password"):
        pass

    langs = model.Language.query.all()
    filter_langs = [x.get_output_dict() for x in langs if x.is_enabled]

    curr_user = model.User.query.filter_by(
        id=util.i(5)).scalar()
    contests = curr_user.contests

    resp = None
    if curr_user:
        resp = curr_user.get_output_dict()

    over_limit_runs_query = model.Run.submit_time >\
                            (datetime.datetime.utcnow() - datetime.timedelta(minutes=5))
    run_count = model.Run.query.filter_by(user_id=curr_user.id)\
                               .filter(over_limit_runs_query)\
                               .count()

    matching_user = model.User.query.filter_by(email="testuser1@example.org").scalar()

    current_user_id = 5
    user = model.User.query.filter_by(id=util.i(current_user_id)).scalar()

    MAX_RUNS = util.get_configuration("max_user_submissions")
    TIME_LIMIT = util.get_configuration("user_submission_time_limit")

    over_limit_runs_query = model.Run.submit_time >\
                            (datetime.datetime.utcnow() - datetime.timedelta(minutes=TIME_LIMIT))
    run_count = model.Run.query.filter_by(user_id=user.id)\
                               .filter(over_limit_runs_query)\
                               .count()

    contest = user.contests[0]

    lang_name = "python"
    problem_slug = "fizzbuzz"
    source_code = "asjdnsadjkasd"*10000
    is_submission = False
    user_test_input = "asdkamdlkamdklas"*10000

    lang = model.Language.query.filter_by(name=lang_name).one()
    problem = model.Problem.query.filter_by(slug=problem_slug).scalar()

    run_input = None
    run_output = None
    if is_submission:
        run_input = problem.secret_input
        run_output = problem.secret_output
    else:
        if user_test_input:
            run_input = user_test_input
        else:
            run_input = problem.sample_input
        run_output = problem.sample_output
    return "good"


@api.route("/signout/<email>", methods=["GET"])
@util.login_required("operator")
def signout_user(email):
    matching_user = model.User.query.filter_by(email=email).scalar()

    if not matching_user:
        return make_response(
            jsonify({
                'error': "Invalid request, couldn't find user"
            }), 400)

    matching_user.merge_metadata({"signout": util.i(time.time())})
    db_session.commit()

    return make_response(jsonify({'status': 'Success'}), 200)


def clean_output_string(s):
    """Cleans up an output string for comparison"""
    return s.replace("\r\n", "\n").strip()


@api.route("/", methods=["GET"])
def index():
    return abort(404)
