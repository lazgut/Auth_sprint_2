import pkgutil
from inspect import isclass

__all__ = []


def _init(__all__):
    """Magic autoload for all marshmallow schemas ending with 'Data'"""
    for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
        _module = loader.find_module(module_name).load_module(module_name)
        for attribute_name in dir(_module):
            # Name convention for marshmallow schema classes - SomethingData
            # I use 'Data' instead of 'Schema' postfix because sqlalchemy classes
            # imported from the package in this case.
            if not attribute_name.endswith('Data'):
                continue
            attribute = getattr(_module, attribute_name)
            if isclass(attribute):
                __all__.append(attribute_name)
                globals()[attribute_name] = attribute


_init(__all__)
