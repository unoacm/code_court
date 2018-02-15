from functools import wraps

import bcrypt

from flask_login import current_user

from flask_sqlalchemy import BaseQuery

from flask import current_app, request, redirect

import model


RUN_CACHE_NAME = 'runcache'
SCORE_CACHE_NAME ='scorecache'


class ModelMissingException(Exception):
    pass


def hash_password(plaintext_password):
    """
    Hashes a password with bcrypt

    Params:
        plaintext_password (str): a plaintext string to be hashed

    Returns:
        str: a bcrpyt hash
    """
    num_rounds = 4

    hashed_password = bcrypt.hashpw(
        plaintext_password.encode("UTF-8"), bcrypt.gensalt(num_rounds))
    return hashed_password.decode("UTF-8")


def is_password_matching(plaintext_password, hashed_password):
    """
    Checks whether a plaintext password matches a bcrypt hashed password

    Params:
        plaintext_password (str): the plaintext password to compare
        hashed_password (str): the bcrypt hashed password to compare

    Returns:
        bool: whether or not the passwords match
    """
    return bcrypt.hashpw(
        plaintext_password.encode(),
        hashed_password.encode()).decode("UTF-8") == hashed_password


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()

            role_ids = [x.name for x in current_user.user_roles]
            if ((role not in role_ids) and (role != "ANY")):
                return current_app.login_manager.unauthorized()

            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


def checkbox_result_to_bool(res):
    """
    Takes in a checkbox result from a form and converts it to a bool

    Params:
        res (str): the result string from a checkbox

    Returns:
        bool: the boolean value of res
    """
    if res == "on":
        return True
    elif res == "off" or res is None:
        return False
    return None


def jwt_identity(payload):
    user_id = payload['identity']

    return model.User.query.filter_by(id=user_id).first()


def get_configuration(key):
    config = model.Configuration.query.filter_by(key=key).scalar()
    val_type = config.valType
    if (val_type == "integer"):
        return int(config.val)
    elif (val_type == "bool"):
        return bool(config.val)
    elif (val_type == "string"):
        return str(config.val)
    else:
        return None


def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("SSL"):
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://", "https://"))

        return fn(*args, **kwargs)

    return decorated_view


def i(num):
    try:
        return int(num)
    except Exception:
        return None


def paginate(sa_query, page, per_page=20, error_out=True):
    sa_query.__class__ = BaseQuery
    return sa_query.paginate(page, per_page, error_out)


def invalidate_cache_item(cache_name, key):
    try:
        import uwsgi
        uwsgi.cache_del(str(key), cache_name)
        uwsgi.cache_clear(cache_name)
    except ImportError:
        pass
