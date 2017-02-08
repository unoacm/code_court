import json
import re
import sqlalchemy

from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for,
)

defendant = Blueprint('defendant', __name__,
                  template_folder='templates')

@defendant.route("/", methods=["GET", "POST"], defaults={'lang_id': None})
@defendant.route("/<int:lang_id>/", methods=["GET"])
def index(lang_id):
    """
    The index page for the defendant frontend
    """

    model = get_model()

    languages = model.Language.query.all()

    selected_language = model.Language.query.filter_by(id=lang_id).all()
    if len(selected_language) == 0:
        current_app.logger.info("Language %s doesn't exist", lang_id)
        abort(400)

    selection = selected_language[0].name
    return render_template("defendant_index.html", languages=languages, selection=selection)



## Util functions
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
