"""Compatibility layer for legacy imports.

This package re-exports selected utilities from ``framework.utils`` so that
legacy code can continue to use imports like::

    from utils.cookie_constants import COOKIE_NAME

Eventually all code should import from ``framework.utils`` directly, but this
shim allows a gradual migration without breaking existing tests.

The module maps every accessed attribute to the corresponding member inside
``framework.utils``.  For junior engineers: think of it as a read-only alias
that forwards import requests to the new location.
"""
from importlib import import_module
from types import ModuleType
import sys as _sys

# List of submodules we want to expose through the legacy ``utils`` namespace.
# Add here only what is required by old tests.
_SUBMODULES = [
    "cookie_constants",
    "auth_utils",
]

_current_module = _sys.modules[__name__]

for _name in _SUBMODULES:
    _new_module = import_module(f"framework.utils.{_name}")
    _sys.modules[f"utils.{_name}"] = _new_module
    setattr(_current_module, _name, _new_module)

# Clean-up internal names
del _name, _new_module, _current_module, _SUBMODULES, import_module, ModuleType, _sys
