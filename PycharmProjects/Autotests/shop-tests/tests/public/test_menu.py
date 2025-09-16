import allure
from allure_commons.types import Severity
from selene.support.shared import browser
from selene import have, be
from befree.api_model import api
from requests import Response


@allure.id("1204")
@allure.title("Женское статичное меню выводится на сайте")
@allure.description("Женское статичное меню выводится на сайте")
@allure.severity(Severity.CRITICAL)
@allure.suite("Menu")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "integrations")
def test_static_female_menu_is_shown(browser_config):
    browser.open("/zhenskaya")
    browser.all("#static-menu div").should(have.size_greater_than(0))


@allure.id("1184")
@allure.title("Мужское статичное меню выводится на сайте")
@allure.description("Мужское статичное меню выводится на сайте")
@allure.severity(Severity.CRITICAL)
@allure.suite("Menu")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "integrations")
def test_static_male_menu_is_shown(browser_config):
    browser.open("/muzhskaya")
    browser.all("#static-menu div").should(have.size_greater_than(0))


@allure.id("1195")
@allure.title("При ховере на статичное меню появляется полная версия меню")
@allure.description("При ховере на статичное меню появляется полная версия меню")
@allure.severity(Severity.CRITICAL)
@allure.suite("Menu")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "ui")
def test_full_menu_enable(browser_config):
    browser.open("/zhenskaya")
    browser.element("#static-menu").hover()


@allure.id("1203")
@allure.title("Пользователь может открыть вложенные уровни меню / 2 уровень")
@allure.description("Пользователь может открыть вложенные уровни меню / 2 уровень")
@allure.severity(Severity.CRITICAL)
@allure.suite("Menu")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "ui")
def test_open_second_menu_level():
    with allure.step("Найти в базе пункт меню со вторым вложенным уровнем"):
        response: Response = api.public_session.get(url="/chains?gender=female&kladr=7800000000000")

    with allure.step("Открыть главную страницу"):
        ...
    with allure.step("Вызвать всплывающее меню"):
        ...
    with allure.step("Кликнуть на пункт меню со вторым вложенным уровнем"):
        ...
    with allure.step("Проверить, что второй уровень открыт"):
        ...


@allure.id("1200")
@allure.title("Пользователь может открыть вложенные уровни меню / 3 уровень")
@allure.description("Пользователь может открыть вложенные уровни меню / 3 уровень")
@allure.severity(Severity.CRITICAL)
@allure.suite("Menu")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "ui")
def test_open_third_menu_level():
    assert False
