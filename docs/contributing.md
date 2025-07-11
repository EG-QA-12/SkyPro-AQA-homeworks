# Руководство по вкату в проект (Contributing Guide)

Этот документ объясняет, как внести изменения в BLL_tests: от клонирования до pull request.

## Шаги для начала работы

1. **Клонируйте репозиторий**:\n   ```bash\n   git clone <repo_url>\n   cd Bll_tests\n   ```\n\n2. **Установите зависимости**:\n   ```bash\n   pip install -r requirements.txt\n   playwright install\n   ```\n\n3. **Создайте ветку**:\n   ```bash\n   git checkout -b feature/new-test\n   ```\n\n4. **Внесите изменения**: Редактируйте файлы, добавьте тесты.\n\n5. **Проверьте локально**:\n   ```bash\n   pytest -v\n   ```\n\n6. **Коммитьте**:\n   ```bash\n   git add .\n   git commit -m 'Добавлен новый тест'\n   ```\n\n7. **Пушьте и создайте PR**:\n   ```bash\n   git push origin feature/new-test\n   ```\n   Затем создайте pull request в GitHub.\n\n## Лучшие практики\n- Используйте осмысленные коммиты.\n- Добавляйте docstrings к коду.\n- Тестируйте изменения перед пушем.\n\nЕсли вопросы — спросите в чате команды! 