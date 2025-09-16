import allure
from allure_commons.types import Severity
from selene.support.shared import browser
from selene import have, be
from selene.api import s, ss
from befree.api_model import api
from requests import Response


@allure.id("1279")
@allure.title("Сортировка листинга 'популярные'")
@allure.description("Изменение сортировки товаров в листинге на 'популярные'")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Public")
@allure.label("layers", "ui")
def test_changing_sorting_in_listing_popular(browser_config):
    with allure.step("Открыть страницу листинга"):
        browser.open("/zhenskaya/platia")

    with allure.step("Проверяем существование листинга"):
        browser.element("div[class*='CatalogList']").should(have.size_greater_than(0))

    # with allure.step("Установить сортировку 'популярные'"):
    # __next > main > section > section.Desktop__Root-sc-12wgrjp-0.qsMYB > div.Settings__Root-vto7kf-0.bVbGaX > div > div
    # __next > main > section > section.Desktop__Root-sc-12wgrjp-0.qsMYB > div.Settings__Root-vto7kf-0.bVbGaX > div > div > ul > div > li.Dropdown__Option-wzcz36-3.jdETZ

    # s("__next > main > section > section.Desktop__Root-sc-12wgrjp-0.qsMYB > div.Settings__Root-vto7kf-0.bVbGaX > div > div").set("__next > main > section > section.Desktop__Root-sc-12wgrjp-0.qsMYB > div.Settings__Root-vto7kf-0.bVbGaX > div > div > ul > div > li.Dropdown__Option-wzcz36-3.jdETZ")
    # with allure.step("Проверяем, что в селекте установилась значение 'популярные'"):
    #     ...
    # with allure.step("Проверяем существование листинга"):
    #     ...
    # with allure.step("Проверяем, что в урле установилось значение sort_id = 1"):
    #     ...
