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

