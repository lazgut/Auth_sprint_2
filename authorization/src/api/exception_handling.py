from http import HTTPStatus

from services.exceptions import ObjectNotFoundException


def handle_obj_not_found(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectNotFoundException as e:
            return {'message': f'{e.args[0]} with id {e.args[1]} not found'}, HTTPStatus.NOT_FOUND
    inner.__name__ = func.__name__  # Because Flask doesn't allow duplicate name 'inner'.
    return inner
