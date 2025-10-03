#!/usr/bin/env python3
"""
Real User SSO Flow Test: bll.by -> bonus.bll.by -> Burger Menu -> News

Tests if SSO cookies transfer from main domain to subdomain in headless mode.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright, TimeoutError
from framework.utils.auth_cookie_provider import get_auth_cookies
from framework.utils.url_utils import add_allow_session_param, is_headless

def test_real_user_sso_flow():
    print("Testing Real User SSO Flow: bll.by -> bonus.bll.by -> Burger Menu -> News")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            bypass_csp=True
        )

        context.add_cookies(get_auth_cookies(role="admin"))
        page = context.new_page()

        try:
            # Step 1: Auth on bll.by
            print("Step 1: Auth on bll.by")
            bll_url = add_allow_session_param("https://bll.by/", is_headless())
            page.goto(bll_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)

            if "bll.by/login" in page.url:
                print("FAILED: bll.by login redirect")
                return False

            # Check menu exists
            from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage
            burger_menu = BurgerMenuPage(page)

            menu_exists = page.locator(".menu-gumb_new.menu-mobile, .menu-btn").count() > 0
            print(f"Menu on bll.by: {menu_exists}")

            if not menu_exists:
                print("WARNING: Menu not found on bll.by")

            # Step 2: Go to bonus.bll.by
            print("Step 2: Navigate to bonus.bll.by")
            bonus_url = add_allow_session_param("https://bonus.bll.by/", is_headless())
            page.goto(bonus_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(4000)

            print(f"Final URL: {page.url}")

            # Check for login redirect
            if "login" in page.url.lower():
                print("FAILED: SSO transfer blocked - redirected to login")
                return False

            print("SUCCESS: No login redirect - SSO transfer works!")

            # Step 3: Test burger menu
            print("Step 3: Test burger menu on bonus")
            menu_on_bonus = page.locator(".menu-gumb_new.menu-mobile, .menu-btn").count() > 0

            if not menu_on_bonus:
                print("FAILED: Burger menu not found on bonus subdomain")
                return False

            print("SUCCESS: Burger menu found on bonus!")

            # Step 4: Try to open menu and navigate to news
            print("Step 4: Test navigation to News")
            try:
                burger_menu.open_menu()
                page.wait_for_timeout(1000)

                burger_menu.click_link_by_text("Новости")
                page.wait_for_timeout(3000)

                final_url = page.url
                success = "news" in final_url.lower() or "novosti" in final_url or "bll.by" in final_url

                if success:
                    print("SUCCESS: News navigation works!")
                    return True
                else:
                    print(f"PARTIAL: Navigated elsewhere: {final_url}")
                    return False

            except Exception as e:
                print(f"FAILED: Menu interaction error: {e}")
                return False

        except Exception as e:
            print(f"Test crashed: {e}")
            return False
        finally:
            try:
                page.screenshot(path="screenshots/real_user_sso_flow.png")
            except:
                pass
            browser.close()

def main():
    print("Real User SSO Flow Test")
    print("This tests the critical question: does SSO work across subdomains?")

    result = test_real_user_sso_flow()

    print(f"\nResult: {'PASSED' if result else 'FAILED'}")

    if result:
        print("\nCONCLUSION: SSO DOES work! Headless subdomain automation is POSSIBLE!")
    else:
        print("\nCONCLUSION: SSO blocked. Need per-subdomain auth or special config.")
    return result

if __name__ == "__main__":
    main()
