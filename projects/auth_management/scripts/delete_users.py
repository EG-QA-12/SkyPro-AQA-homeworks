import os
import sys

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.user_manager import UserManager

def main():
    user_manager = UserManager()
    users_to_delete = ['user01', 'user05', 'user08']

    for user_login in users_to_delete:
        if user_manager.get_user(user_login):
            user_manager.delete_user(user_login)
            print(f"Пользователь {user_login} удален.")
        else:
            print(f"Пользователь {user_login} не найден.")

    print("Удаление завершено.")

if __name__ == "__main__":
    main()
