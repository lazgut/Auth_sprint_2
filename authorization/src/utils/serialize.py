import typing as t

import schemas
from db import db


def serialize(obj: t.Any):
    if isinstance(obj, list) and len(obj):
        m = _get_serializer(obj[0], True)
    else:
        m = _get_serializer(obj)

    if m:
        return m.dump(obj)

    return obj


def _get_serializer(obj: t.Any, many: bool = False):
    if isinstance(obj, db.Model):
        # Name convention for marshmallow schema classes - SomethingData
        # I use 'Data' instead of 'Schema' postfix because sqlalchemy classes
        # imported from 'schemas' package in this case.
        # See magic autoloader in schemas.__init__.py
        schema_class = '{0}Data'.format(obj.__class__.__name__[0:-5])
        return getattr(schemas, schema_class)(many=many)
