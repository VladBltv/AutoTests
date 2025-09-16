import os
from befree.api_model.test_data.listing import prepared_data
from utils import attachments, database
import allure
import pytest
from selene.support.shared import browser
from selenium import webdriver
from dotenv import load_dotenv
from befree.api_model.esb import EsbPublic
from utils import helpers
from playwright.sync_api import Page, sync_playwright
from befree.ui_model.shop import ShopPages
from befree.ui_model.shop.product.product_page import ProductPage
from befree.api_model.catalog.db_queries.queries import QueriesCatalog

DEFAULT_BROWSER_VERSION = "118"


def pytest_addoption(parser):
    parser.addoption("--browser_version", default="118")
    parser.addoption("--host", default="remote")
    parser.addoption("--base_url", default="https://befree.ru")


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()


with allure.step("Configure browser context"):
    @pytest.fixture(scope="function")
    def shop_page(request) -> Page:
        """
        Фикстура для создания страницы Playwright с поддержкой десктопной и мобильной версии.
        Фикстура самостоятельно создаёт браузер, контекст и страницу с помощью sync_playwright().
        Она не зависит от внешней фикстуры page.
        Для мобильной версии: используем p.devices["iPhone 12"] для эмуляции устройства.
        Для десктопной: обычный контекст.
        Параметризация через request.param: если тест помечен как мобильный, передаётся True.

        По умолчанию: десктопная версия.
        Для мобильной версии: @pytest.mark.parametrize("shop_page", [True], indirect=True), где значение indirect
        отвечает именно за мобильную версию
        """
        mobile = getattr(request, "param", False)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)

            if mobile:
                # Мобильная версия: эмуляция iPhone 15
                iphone_15 = p.devices["iPhone 15"]
                context = browser.new_context(**iphone_15, base_url=os.getenv("SHOP_URL"))
            else:
                # Десктопная версия: обычный контекст
                context = browser.new_context(base_url=os.getenv("SHOP_URL"))

            page = context.new_page()
            yield page

            # Закрываем ресурсы
            page.close()
            context.close()
            browser.close()


    @pytest.fixture(scope="function")
    def shop(shop_page: Page):
        """
        Фикстура для предоставления объекта ShopPages с инициализированными страницами.
        """
        # Отключаем штору о принятии кук (как в вашем примере)
        cookie_accepted = helpers.cookies_for_shop(name="cookie_accepted", value="1")
        shop_page.context.add_cookies([cookie_accepted])

        return ShopPages(shop_page)



with allure.step("Configure browser"):
    @pytest.fixture(scope="function")
    def browser_config(request):
        host = request.config.getoption("--host")
        if host == "local":
            browser_version = request.config.getoption("--browser_version")
            browser_version = browser_version if browser_version != "" else DEFAULT_BROWSER_VERSION
            selenoid_capabilities = {
                "browserName": "chrome",
                "browserVersion": browser_version,
                "selenoid:options": {"enableVNC": True, "enableVideo": True},
            }

            login = os.getenv("SELENOID_LOGIN")
            password = os.getenv("SELENOID_PASSWORD")

            driver = webdriver.Remote(
                command_executor=f"https://{login}:{password}@selenoid.befree.ru/wd/hub",
                desired_capabilities=selenoid_capabilities,
            )

            browser.config.driver = driver

        browser.config.base_url = os.getenv("SHOP_URL")
        browser.config.window_width = 1440
        browser.config.window_height = 768

        yield browser

        attachments.add_html(browser)
        attachments.add_screenshot(browser)
        attachments.add_logs(browser)
        attachments.add_video(browser)
        browser.quit()


with allure.step("Cocreate configure browser"):
    @pytest.fixture(scope="function")
    def cocreate_browser_config(request):
        host = request.config.getoption("--host")
        if host == "local":
            browser_version = request.config.getoption("--browser_version")
            browser_version = browser_version if browser_version != "" else DEFAULT_BROWSER_VERSION
            selenoid_capabilities = {
                "browserName": "chrome",
                "browserVersion": browser_version,
                "selenoid:options": {"enableVNC": True, "enableVideo": True},
            }

            login = os.getenv("SELENOID_LOGIN")
            password = os.getenv("SELENOID_PASSWORD")

            driver = webdriver.Remote(
                command_executor=f"https://{login}:{password}@selenoid.befree.ru/wd/hub",
                desired_capabilities=selenoid_capabilities,
            )

            browser.config.driver = driver

        browser.config.base_url = os.getenv("COCREATE_URL")
        browser.config.window_width = 1440
        browser.config.window_height = 768

        yield browser

        attachments.add_html(browser)
        attachments.add_screenshot(browser)
        attachments.add_logs(browser)
        attachments.add_video(browser)
        browser.quit()


with allure.step("Подготовка тестовых товаров для ордерс"):

    @pytest.fixture(scope="function")
    def goods():
        # отправка запроса в модуль актуальных остатков
        stocks = EsbPublic.api_esb.esb_stocks()
        assert stocks.status_code == 200

        variations = {}

        # поиск товара с qty = 2
        variations["qty_2"] = dict(helpers.find_by_qty(stocks.json(), "quantity", 2))

        return variations


with allure.step("Подготовка БД каталога к тестам, генерация данных"):
    @pytest.fixture(scope="function", autouse=False)
    def prepare_catalog_database():
        # заполнение variations
        database.filling_out_table(data=prepared_data.tables["variations"], service="catalog")

        # заполнение products
        database.filling_out_table(data=prepared_data.tables["products"], service="catalog")

with allure.step("Подключение к БД"):
    @pytest.fixture(scope='function')
    def init_db_queries():
        return QueriesCatalog()

with allure.step("Возвращает экземпляр класса ProductPage"):
    @pytest.fixture(scope='function')
    def init_product_page(shop_page, init_db_queries):
        return ProductPage(shop_page)