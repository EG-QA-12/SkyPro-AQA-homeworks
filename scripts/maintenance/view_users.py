import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from projects.auth_management.user_manager import UserManager
from projects.auth_management.logger import setup_logger

logger = setup_logger(__name__)


def main():
    logger.info("Запуск скрипта view_users.py")
    user_manager = UserManager()
    users = user_manager.get_all_users()

    if users:
        logger.info("Список пользователей в базе данных:")
        for user in users:
            logger.info(user)
    else:
        logger.info("В базе данных нет пользователей.")


if __name__ == "__main__":
    main()

