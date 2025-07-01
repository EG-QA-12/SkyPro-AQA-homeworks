"""Legacy import shim for ``allure_utils``.

Several old tests use::

    from allure_utils import ui_test

The real implementation now lives in ``framework.utils.allure_utils``.  This
thin wrapper simply re-exports everything so that legacy tests continue to
work.  New code SHOULD import from ``framework.utils.allure_utils`` directly.
"""
from importlib import import_module
import sys as _sys

_real_module = import_module("framework.utils.allure_utils")
_sys.modules[__name__] = _real_module
