"""Legacy import shim for ``auth_utils``.

Old tests import helpers directly::

    from auth_utils import save_cookie

Реальная реализация перенесена в ``framework.utils.auth_utils``.  Этот файл
позволяет старым тестам работать без изменения кода.

Junior note: Мы просто «переадресовываем» модуль.  Если зайти в исходники,
вы увидите, что здесь почти нет кода, а всё настоящее содержимое находится в
новом месте.  Так мы постепенно переведём все импорты на новую структуру.
"""
from importlib import import_module
import sys as _sys

_real_module = import_module("framework.utils.auth_utils")
_sys.modules[__name__] = _real_module
