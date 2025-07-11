from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field


# Определяем путь к корневой директории проекта для корректной работы с файлами
BASE_DIR = Path(__file__).resolve().parent.parent

# Исправляем путь к файлу с переменными окружения: используем secrets/creds.env
dotenv_path = Path("D:/Bll_tests/secrets/creds.env")

# Загрузка переменных окружения из .env файла с проверкой наличия файла
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, encoding='utf-8', verbose=False)

# Конфигурация проекта — валидируется pydantic
class AppConfig(BaseSettings):
    """
    Настройки проекта, загружаемые из переменных окружения или файла `.env`.
    Поля LOGIN, PASS обязательны.
    """

    # Credentials
    LOGIN: str = Field(default="test_user", env="LOGIN")
    PASS: str = Field(default="test_password", env="PASS")

    # Browser
    HEADLESS: bool = Field(default=False, env="HEADLESS")

    # URLs
    LOGIN_URL: str = Field(default="https://ca.bll.by/login", env="LOGIN_URL")
    TARGET_URL: str = Field(default="https://ca.bll.by/", env="TARGET_URL")
    BASE_URL: str = Field(default="https://ca.bll.by", env="BASE_URL")

    # Admin credentials
    ADMIN_LOGIN: str = Field(default="admin", env="ADMIN_LOGIN")
    ADMIN_PASS: str = Field(default="admin123", env="ADMIN_PASS")
    ADMIN_ID: str = Field(default="000001", env="ADMIN_ID")
    ADMIN_EMAIL: str = Field(default="admin@example.com", env="ADMIN_EMAIL")
    ADMIN_PHONE: str = Field(default="+1234567890", env="ADMIN_PHONE")

    # Moderator credentials
    MODERATOR_LOGIN: str = Field(default="moderator", env="MODERATOR_LOGIN")
    MODERATOR_PASS: str = Field(default="moderator123", env="MODERATOR_PASS")
    MODERATOR_ID: str = Field(default="000002", env="MODERATOR_ID")
    MODERATOR_EMAIL: str = Field(default="moderator@example.com", env="MODERATOR_EMAIL")
    MODERATOR_PHONE: str = Field(default="+1234567891", env="MODERATOR_PHONE")

    # Expert credentials
    EXPERT_LOGIN: str = Field(default="expert", env="EXPERT_LOGIN")
    EXPERT_PASS: str = Field(default="expert123", env="EXPERT_PASS")
    EXPERT_ID: str = Field(default="287242", env="EXPERT_ID")
    EXPERT_EMAIL: str = Field(default="expert@example.com", env="EXPERT_EMAIL")
    EXPERT_PHONE: str = Field(default="+1234567892", env="EXPERT_PHONE")

    # User credentials
    USER_LOGIN: str = Field(default="user", env="USER_LOGIN")
    USER_PASS: str = Field(default="user123", env="USER_PASS")
    USER_ID: str = Field(default="000004", env="USER_ID")
    USER_EMAIL: str = Field(default="user@example.com", env="USER_EMAIL")
    USER_PHONE: str = Field(default="+1234567893", env="USER_PHONE")
    USER_ROLE: str = Field(default="user", env="USER_ROLE")

    # Paths
    CREDS_PATH: Path = Path(dotenv_path)
    COOKIES_PATH: Path = Path("D:/Bll_tests/cookies/cookies.json")
    DB_PATH: Path = BASE_DIR / "data" / "users.db"

    # Bulk CSV for массовое создание тестовых аккаунтов
    BULK_CSV_PATH: Path = Path("D:/Bll_tests/secrets/bulk_users.csv")

    # Logging
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "auth_project.log"
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_PATH: str = Field(default="logs/app.log", env="LOG_PATH")

    class Config:
        env_file = dotenv_path
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Разрешаем дополнительные поля


# Экземпляр настроек, импортируемый в других модулях
config = AppConfig()  # type: ignore
