import sys

from functools import wraps

import bcrypt

from flask_login import current_user

from flask import current_app

class ModelMissingException(Exception):
    pass

def get_model():
    """
    Gets the model from the current app,

    Note:
        must be called from within a request context

    Raises:
        ModelMissingException: if the model is not accessible from the current_app

    Returns:
        the model module
    """
    model = current_app.config.get('model')
    if model is None:
        raise ModelMissingException()
    return model

def hash_password(plaintext_password):
    """
    Hashes a password with bcrypt

    Params:
        plaintext_password (str): a plaintext string to be hashed

    Returns:
        str: a bcrpyt hash
    """
    if current_app.config.get('TESTING'):
        # reduce number of rounds for quicker tests
        num_rounds = 4
    else:
        num_rounds = 12

    hashed_password = bcrypt.hashpw(plaintext_password.encode("UTF-8"), bcrypt.gensalt(num_rounds))
    return hashed_password

def is_password_matching(plaintext_password, hashed_password):
    """
    Checks whether a plaintext password matches a bcrypt hashed password

    Params:
        plaintext_password (str): the plaintext password to compare
        hashed_password (str): the bcrypt hashed password to compare

    Returns:
        bool: whether or not the passwords match
    """
    try:
        return bcrypt.hashpw(str(plaintext_password), str(hashed_password)) == hashed_password
    except:
        return bcrypt.hashpw(plaintext_password.encode(), hashed_password) == hashed_password

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
              return current_app.login_manager.unauthorized()

            role_ids = [x.id for x in current_user.user_roles]
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