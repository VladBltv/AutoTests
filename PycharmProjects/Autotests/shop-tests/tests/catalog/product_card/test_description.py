import os
from playwright.sync_api import expect
from befree.ui_model.shop.product.locators import Locators
import re
from urllib.parse import urljoin
import allure
from allure_commons.types import Severity

@allure.id("3032")
@allure.tag("UI Tests")
@allure.severity(Severity.MINOR)
@allure.suite("Product")
@allure.label("owner", "Bolotov")
@allure.description("Проверяем, что все аккордеоны закрыты при открытии страницы")
@allure.title("Аккордеоны закрыты")
@allure.label("service", "Public")
def test_accordions_closed(init_db_queries, shop_page, shop, init_product_page):
    """
    Проверяет что все аккордеоны закрыты и прокликиваются
    """
    product_info = init_db_queries.get_product_by_conditions(["title LIKE 'брюки женские'"])
    shop_page.goto(f'{os.getenv("SHOP_URL")}/zhenskaya/product/{product_info["article"]}')
    init_product_page.accordions_closed()


@allure.id("3032")
@allure.tag("UI Tests")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Bolotov")
@allure.description("Проверяет что блок с описанием отображается, даже если пустой и в нем нет текста")
@allure.title("Пустое описание отображается")
@allure.label("service", "Public")
def test_empty_description(init_db_queries, init_product_page, shop_page, shop):
    """
    Проверяет что блок с описанием отображается, даже если пустой и в нем нет текста
    """
    loc = Locators(shop_page)
    article_dict = init_db_queries.get_empty_description_product()
    article = article_dict['article']
    shop_page.goto(f"{os.getenv('SHOP_URL')}/zhenskaya/product/{article}")
    init_product_page.accordions_closed()
    element = loc.description
    close_style = element.locator('[style]')
    description_attributes = close_style.locator('div[data-bui-id="Typography"]')
    count = description_attributes.count()
    description_text = description_attributes.nth(count-1)
    expect(description_text).not_to_be_visible()
    product_attributes = init_product_page.take_attributes_from_description()
    expect(product_attributes).to_have_count(3)

@allure.id("3032")
@allure.tag("UI Tests")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Bolotov")
@allure.description("Проверяет кликабельность гиперссылок в описании")
@allure.title("Гиперссылки в описании работают")
@allure.label("service", "Public")
def test_hyperlink_in_description(init_db_queries, init_product_page, shop_page, shop):
    """
    Проверяет кликабельность гиперссылок в описании
    """
    article_dict = init_db_queries.get_description_with_hyperlink()
    shop_page.goto(f"{os.getenv('SHOP_URL')}/zhenskaya/product/{article_dict['article']}")
    init_product_page.accordions_closed()
    product_attributes = init_product_page.take_attributes_from_description()
    count = product_attributes.count()
    description_element = product_attributes.nth(count-1)
    description_element_link = description_element.locator('a[href]')
    if description_element_link.count() == 0:
        raise AssertionError("Ссылка в описании не найдена")

    href = description_element_link.nth(0).get_attribute('href')
    expected_url = urljoin(shop_page.url, href)

    description_element_link.nth(0).click()
    expect(shop_page).to_have_url(re.compile(f"^{re.escape(expected_url)}"))

@allure.id("3032")
@allure.tag("UI Tests")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Bolotov")
@allure.description("Проверяет что спецсимволы отображаются корректно")
@allure.title("Спецсимволы корректно отображаются")
@allure.label("service", "Public")
def test_special_symbols_on_description(init_db_queries, init_product_page, shop, shop_page):
    """
    Проверяет что спецсимволы отображаются корректно
    """
    article_dict = init_db_queries.get_description_with_special_symb()
    shop_page.goto(f"{os.getenv('SHOP_URL')}/zhenskaya/product/{article_dict['article']}")
    init_product_page.accordions_closed()

    product_attributes = init_product_page.take_attributes_from_description()
    count = product_attributes.count()
    description_text = product_attributes.nth(count-1)

    special_symbols = ['"', "'", '<', '>', '%', '$', '#', '@', '!', '?', '\\', '/', '[', ']', '(', ')', '{', '}', ';',
                       ':']

    regex_pattern = ''.join(re.escape(s) for s in special_symbols)
    regex = re.compile(f"[{regex_pattern}]")

    expect(description_text).to_contain_text(regex)