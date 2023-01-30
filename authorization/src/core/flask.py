from flask import Flask as BaseFlask
from utils.serialize import serialize


class Flask(BaseFlask):
    # override method to allow return sqlalchemy model objects from view functions
    def make_response(self, rv):
        if isinstance(rv, tuple):
            rv = list(rv)
            # suppose body, status, header tuple here
            rv[0] = serialize(rv[0])
            rv = tuple(rv)
        else:
            rv = serialize(rv)
        return super().make_response(rv)
