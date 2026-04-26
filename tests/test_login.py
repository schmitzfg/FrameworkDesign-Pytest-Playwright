"""
Test Case: User Login Functionality

====================================
Test Steps
====================================

Test Case 1: Verify Login with Invalid Credentials
--------------------------------------------------
1. Open the application in the browser.
2. Navigate to the "My Account" menu on the Home page.
3. Click on the "Login" link.
4. Enter an invalid email adress and password.
5. Click on the "Login" button.
6. Verify that an error message appears indicating invalid credentials.

Expected Results:
-----------------
An error message should be displayed, and the user should not be logged in.


Test Case 2: Verify Login with Valid Credentials.
-------------------------------------------------
1. Open the application in the browser.
2. Navigate to the "My Account" menu on the Home page.
3. Click on the "Login" link.
4. Enter an invalid email adress and password.
5. Click on the "Login" button.
6. Verify that "My Account" page is displayed after scuccessful login.

Expected Results:
-----------------
The "My Account" page should appear, confirming a successfull login.
"""

import pytest
import time
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.my_account_page import MyAccountPage
from playwright.sync_api import expect
from config import Config

@pytest.mark.regression
def test_invalid_user_login(page):
    home_page = HomePage(page)
    login_page = LoginPage(page)

    home_page.click_my_account()
    home_page.click_login()

    login_page.set_email(Config.invalid_email)
    login_page.set_password(Config.invalid_password)
    login_page.click_login()

    time.sleep(3)

    expect(login_page.get_login_error()).to_be_visible(timeout=3000)
    



@pytest.mark.sanity
def test_valid_user_login(page):
    home_page = HomePage(page)
    login_page = LoginPage(page)
    my_account_page = MyAccountPage(page)

    home_page.click_my_account()
    home_page.click_login()

    login_page.set_email(Config.email)
    login_page.set_password(Config.password)
    login_page.click_login()

    time.sleep(3)

    expect(my_account_page.get_my_account_page_heading()).to_be_visible(timeout=3000)