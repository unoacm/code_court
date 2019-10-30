import util
from flask import (
    Blueprint,
    render_template,
    request,
)

import random
import model
from database import db_session

utils = Blueprint("utils", __name__, template_folder="templates/utils")

@utils.route("/random-contestants/", methods=["GET"])
@util.login_required("operator")
def random_contestants():
    """
    Displays a randomized list of contestants
    """
    contestants = model.User.query.filter(model.User.user_roles.any(name="defendant")).all()

    num = int(request.args.get('n')) or len(contestants)
    if num > len(contestants):
        num = len(contestants)

    shuffled_contestants = random.sample(contestants, k=num)
    return render_template("utils/random-contestants.html", contestants=shuffled_contestants)

@utils.route("/invalidate-caches/", methods=["GET"])
@util.login_required("operator")
def invalidate_caches():
    """
    Invalidates all uwsgi caches
    """
    util.invalidate_cache(util.RUN_CACHE_NAME)
    util.invalidate_cache(util.SCORE_CACHE_NAME)
    return render_template("message.html", message="Invalidated cache")
