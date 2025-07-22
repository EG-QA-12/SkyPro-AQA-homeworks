import pytest
from pathlib import Path
import json
import requests
import csv
import re
from framework.utils.auth_cookie_provider import get_auth_cookies

CSV_PATH = Path("scripts/data/burger_menu_links_admin.csv")
COOKIES_PATH = Path("cookies/admin_cookies.json")

# Загрузка ссылок
links = []
with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        links.append((row["Текст ссылки"].strip(), row["URL"].strip()))

# Загрузка куки для Admin (берём только test_joint_session)
admin_cookies = get_auth_cookies(role="admin")

@pytest.mark.parametrize("link_text,url", links)
def test_burger_menu_link_requests(link_text, url):
    if url.startswith("tel:"):
        assert url.startswith("tel:"), f"tel: ссылка некорректна: {url}"
        return
    response = requests.get(url, cookies=admin_cookies, timeout=10)
    assert response.status_code == 200, f"Статус-код не 200 для {url}"
    # Парсим заголовок (h1/h2/h3)
    m = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", response.text, re.IGNORECASE | re.DOTALL)
    assert m, f"Заголовок не найден на {url}"
    header = m.group(1).strip()
    assert link_text.lower() in header.lower(), f"Заголовок '{header}' не содержит '{link_text}'" 