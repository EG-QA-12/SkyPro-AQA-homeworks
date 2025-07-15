# 📊 Отчет об анализе структуры импортов

**Дата анализа:** D:\Bll_tests
**Проанализировано файлов:** 2009
**Модулей в графе:** 2009
**Найдено циклов:** 0

## 📈 Общая статистика

- **Всего импортов:** 157
- **Модулей с импортами:** 85

### 🔝 Топ модулей по количеству зависимостей

- **projects.auth_management.auth_gui_new**: 6 импортов
- **tests.unit.test_auth_quick**: 5 импортов
- **projects.auth_management.auth_gui**: 5 импортов
- **projects.auth_management.tests.e2e.general.test_main_page_admin**: 5 импортов
- **tests.auth.test_ui_login_and_session_save**: 4 импортов
- **tests.visual.test_cookie_auth_visual**: 4 импортов
- **projects.auth_management.clean_database**: 4 импортов
- **projects.auth_management.show_admin_auth**: 4 импортов
- **projects.auth_management.reports.cookie_auth_report**: 4 импортов
- **projects.auth_management.scripts.clean_db**: 4 импортов
## 🏗️ Анализ структуры

### Framework зависимости

- **framework.utils.auth_operations**: framework.app.pages.login_page, framework.utils.auth_utils, framework.utils.cookie_constants, framework.utils.url_utils
- **framework.utils.db_helpers**: framework.db_utils.database_manager
- **framework.app.pages.login_page**: framework.app.pages.base_page, framework.utils.cookie_constants
- **framework.app.pages.moderator_dashboard_page**: framework.utils.url_utils
- **framework.app.pages.profile_page**: framework.utils.url_utils

## 💡 Рекомендации по оптимизации

### 🔧 Общие улучшения

1. **Ленивые импорты** - импорт внутри функций для тяжелых зависимостей
2. **Условные импорты** - try/except для опциональных зависимостей
3. **Модульная архитектура** - четкое разделение слоев приложения
