# ПЛАН ОЧИСТКИ УСТАРЕВШИХ ФАЙЛОВ

## 1. Batch файлы для удаления:
- `scripts\maintenance\run_csv_auth_gui.bat` - broken
  - Ссылается на несуществующие файлы
- `projects\auth_management\run_mass_cookie_test.bat` - temporary
- `projects\auth_management\test_admin_cookies.bat` - temporary
- `projects\auth_management\test_visual_auth.bat` - temporary

## 2. README файлы для консолидации:

## 3. Рекомендации:
- Удалить broken/temporary batch файлы
- Объединить информацию из минимальных README в основной
- Оставить только функциональные скрипты
