# Анализ UI Локаторов сайта BLL.BY

## Общая информация
- **Дата анализа**: 23.09.2025
- **URL сайта**: https://bll.by
- **Всего элементов найдено**: 22
- **Файл с локаторами**: ui_locators_bll_by.json

## Структура основных элементов

### 1. Шапка сайта (Header)
```json
{
  "tagName": "header",
  "attributes": {
    "class": "page-header page-header_mp"
  }
}
```

### 2. Навигационное меню
```json
{
  "tagName": "div",
  "attributes": {
    "class": "menu-gumb_new menu-mobile"
  }
}
```

### 3. Основное меню рубрик
```json
{
  "tagName": "div",
  "attributes": {
    "class": "new-menu new-menu_main"
  }
}
```

## Ключевые UI элементы

### Меню-бургер
```json
{
  "tagName": "a",
  "attributes": {
    "class": "menu-btn menu-btn_new",
    "href": "#"
  }
}
```

### Иконка бургер-меню
```json
{
  "tagName": "span",
  "attributes": {
    "class": "burger-icon"
  }
}
```

### Основные рубрики
1. **Новости**
   ```json
   {
     "tagName": "a",
     "attributes": {
       "class": "menu_item_link link-rubric_1",
       "href": "https://bll.by/news"
     },
     "text": "Новости"
   }
   ```

2. **Справочная информация**
   ```json
   {
     "tagName": "a",
     "attributes": {
       "class": "menu_item_link link-rubric_2",
       "href": "https://bll.by/docs/spravochnaya-informatsiya-200083"
     },
     "text": "Справочная"
   }
   ```

3. **Кодексы**
   ```json
   {
     "tagName": "a",
     "attributes": {
       "class": "menu_item_link link-rubric_3",
       "href": "https://bll.by/docs/kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580"
     },
     "text": "Кодексы"
   }
   ```

## Рекомендации по использованию локаторов

### 1. Для автоматизации тестирования
- Использовать `data-testid` атрибуты (если будут добавлены)
- Приоритет классов: `menu_item_link` → `menu-btn` → `burger-icon`
- Уникальные идентификаторы: `link-rubric_1`, `link-rubric_2`, `link-rubric_3`

### 2. Для Playwright тестов
```javascript
// Клик по бургер-меню
await page.click('.menu-btn.menu-btn_new');

// Переход по ссылке "Новости"
await page.click('.menu_item_link.link-rubric_1');

// Проверка видимости элементов
await expect(page.locator('.new-menu_main')).toBeVisible();
```

### 3. Для Selenium тестов
```python
# Поиск бургер-меню
burger_menu = driver.find_element(By.CSS_SELECTOR, ".menu-btn.menu-btn_new")

# Поиск рубрик по классам
news_link = driver.find_element(By.CSS_SELECTOR, ".menu_item_link.link-rubric_1")
```

## Заключение

Анализ показал, что сайт BLL.BY имеет хорошо структурированную систему навигации с четкой иерархией классов. Основные элементы навигации легко идентифицируются по уникальным классам, что делает их пригодными для автоматизации тестирования.

Рекомендуется:
1. Добавить `data-testid` атрибуты для ключевых элементов
2. Использовать текущие классы для создания стабильных локаторов
3. Регулярно обновлять локаторы при изменениях в дизайне сайта
