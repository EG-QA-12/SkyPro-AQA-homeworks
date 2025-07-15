#!/usr/bin/env python
"""Bulk authorize users from a CSV file and cache their cookies in the database.

Usage:
    python scripts/authorize_users_from_csv.py users.csv [--db path/to/db] [--headless]

CSV columns (header row required):
    login,password,role,email,phone
Only login and password are mandatory; other fields are optional.
"""
import argparse
import os
import sys

# Add project root to sys.path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from projects.auth_management.user_manager import UserManager  # noqa: E402
from projects.auth_management.logger import setup_logger  # noqa: E402

logger = setup_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk authorize users from CSV and cache cookies")
    parser.add_argument("csv_path", help="Path to CSV file with user credentials")
    parser.add_argument("--db", dest="db_path", help="Path to SQLite DB (optional)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--relogin", action="store_true", help="Принудительно переавторизовать пользователей, игнорируя кэш")
    args = parser.parse_args()

    if not os.path.exists(args.csv_path):
        logger.error("CSV file %s not found", args.csv_path)
        sys.exit(1)

    manager = UserManager(args.db_path) if args.db_path else UserManager()
    summary = manager.authorize_users_from_csv(args.csv_path, headless=args.headless, force_reauth=args.relogin)

    logger.info("Authorization finished. Success: %d, Failed: %d", len(summary['success']), len(summary['failed']))
    if summary["failed"]:
        logger.warning("Failed users: %s", ", ".join(summary["failed"]))


if __name__ == "__main__":
    main()
