# pylint: disable=unused-import
"""Proxy-модуль.

Исторически DatabaseManager был определён и здесь, и в ``framework.db_utils``.
Чтобы оставить обратную совместимость (`from projects.auth_management.database import DatabaseManager`)
и при этом перейти на единую реализацию, мы просто реэкспортируем класс из
фреймворка. При необходимости все доработки делаем в одном месте —
``framework/db_utils/database_manager.py``.
"""

from framework.db_utils.database_manager import DatabaseManager  # noqa: F401
