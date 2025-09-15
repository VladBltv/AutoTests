import pytest
from playwright.sync_api import expect, Playwright
from locators.register_page import Locators


@pytest.fixture(scope='session')
def initialize_browser_state(playwright: Playwright):
    print('Фикстура на регистрацию запущена')
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    locator = Locators(page)
    page.goto('https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/registration')
    locator.email_input.fill('user@gmail.com')
    locator.username_input.fill('username')
    locator.password_input.fill('password')
    expect(locator.register_button).to_be_visible()
    locator.register_button.click()
    expect(locator.auth_title).to_have_text('Dashboard')
    context.storage_state(path='browser-state.json')

@pytest.fixture(scope='function')
def chromium_page_with_state(playwright: Playwright):
    print("Фикстура на получение авторизованной сессии")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state='browser-state.json')
    yield context.new_page()

@pytest.fixture(params=[1,2])
def testfixture(request):
    print(request.param)