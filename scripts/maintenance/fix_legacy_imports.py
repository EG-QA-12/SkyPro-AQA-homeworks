import pathlib
import re

FILES = [
    r"tests/auth/test_authentication.py",
    r"tests/conftest.py",
    r"tests/e2e/conftest.py",
    r"tests/e2e/redirect_tests/conftest.py",
    r"tests/e2e/redirect_tests/test_redirect_status_codes.py",
    r"tests/e2e/test_cookie_auth.py",
    r"tests/e2e/test_updated_auth_demo.py",
    r"tests/e2e/test_ui_login_and_session_save.py",
    r"tests/e2e/user_journeys/test_main_page_access.py",
    r"tests/integration/conftest.py",
    r"tests/integration/infrastructure/conftest.py",
    r"tests/integration/infrastructure/test_redirects.py",
]

REPLACEMENTS = [
    (re.compile(r"from\\s+allure_utils(\\s+import|\\s+as|\\s*$)"), r"from framework.utils.reporting.allure_utils\\1"),
    (re.compile(r"from\\s+auth_utils(\\s+import|\\s+as|\\s*$)"), r"from framework.utils.auth_utils\\1"),
]

for rel_path in FILES:
    path = pathlib.Path(rel_path)
    if not path.exists():
        print(f"File not found: {rel_path}")
        continue
    text = path.read_text(encoding="utf-8")
    orig = text
    for pattern, repl in REPLACEMENTS:
        text = pattern.sub(repl, text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        print(f"Updated: {rel_path}")
    else:
        print(f"No changes: {rel_path}")
