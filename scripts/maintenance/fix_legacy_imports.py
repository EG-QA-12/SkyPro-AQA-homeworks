import argparse
import pathlib
import re
import sys
from typing import List

EXCLUDE_DIRS = {'.git', 'venv', '__pycache__'}
DEFAULT_PATTERNS = [
    # Замена `from src.<module>` на `from <module>`
    (re.compile(r"(from\s+)src\.(\w+)"), r"\1\2"),
    # Замена `import src.<module>` на `import <module>`
    (re.compile(r"(import\s+)src\.(\w+)"), r"\1\2"),
    # Замена `from src.<package>.<module>` на `from <package>.<module>`
    (re.compile(r"(from\s+)src\.([\w\.]+)"), r"\1\2"),
]

LEGACY_SPECIFIC = [
    # То, что уже было раньше
    (re.compile(r"from\s+allure_utils(\s+import|\s+as|\s*$)"), r"from framework.utils.reporting.allure_utils\\1"),
    (re.compile(r"from\s+auth_utils(\s+import|\s+as|\s*$)"), r"from framework.utils.auth_utils\\1"),
]

REPLACEMENTS = DEFAULT_PATTERNS + LEGACY_SPECIFIC

def iter_python_files(root: pathlib.Path) -> List[pathlib.Path]:
    """Рекурсивно обходит каталог, игнорируя EXCLUDE_DIRS, и возвращает список .py файлов."""
    for path in root.rglob('*.py'):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path

def process_file(path: pathlib.Path) -> bool:
    """Применяет все замены к файлу. Возвращает True, если были изменения."""
    text = path.read_text(encoding='utf-8')
    orig = text
    for pattern, repl in REPLACEMENTS:
        text = pattern.sub(repl, text)
    if text != orig:
        path.write_text(text, encoding='utf-8')
        print(f"✅ Updated: {path.relative_to(PROJECT_ROOT)}")
        return True
    return False

parser = argparse.ArgumentParser(description="Fix legacy imports (src.*) across the project.")
parser.add_argument('--root', default='..', help='Project root to scan (default: parent directory)')
args = parser.parse_args()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.joinpath(args.root).resolve()
if not PROJECT_ROOT.exists():
    sys.exit(f"Root '{PROJECT_ROOT}' does not exist")

changed = 0
for file_path in iter_python_files(PROJECT_ROOT):
    if process_file(file_path):
        changed += 1

print(f"\nDone. {changed} file(s) updated.")

