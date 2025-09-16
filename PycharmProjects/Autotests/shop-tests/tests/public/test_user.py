import allure
from allure_commons.types import Severity
from selene.support import by
from selene.support.shared import browser
from selene import have, be
from selene.support.shared.jquery_style import s

from befree.api_model import api
from requests import Response
from mimesis import Person, Datetime


@allure.id("2714")
@allure.title("Успешная авторизация существующего пользователя")
@allure.description("Проверяем, что пользователь успешно авторизуется в ЛК")
@allure.severity(Severity.CRITICAL)
@allure.suite("Account")
@allure.label("feature", "Авторизация пользователя")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "ui")
def test_successful_auth(browser_config):
    with allure.step("Перейти на сайт"):
        browser.open("/zhenskaya")

    with allure.step("Открыть форму авторизации"):
        browser.element(".sc-ba702bc9-1").click()

    with allure.step("Ввести email существующего пользователя"):
        browser.element("input[type='email']").click().type("melon.test.2@yandex.ru")

    with allure.step("Ввести пароль существующего пользователя"):
        browser.element("input[type='password']").click().type("aA123456")

    with allure.step("Отправить форму"):
        browser.element(by.text("продолжить")).click()

    with allure.step("Успешная авторизация. ЛК доступен"):
        browser.element(".sc-ba702bc9-1").click()
        browser.element(by.text("управление аккаунтом")).should(be.present)


@allure.id("2713")
@allure.title("Успешная регистрация существующего пользователя")
@allure.description("Проверяем, что пользователь успешно регистрируется в ЛК")
@allure.severity(Severity.CRITICAL)
@allure.suite("Account")
@allure.label("feature", "Авторизация регистрация")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.label("layers", "ui")
def test_successful_registration(browser_config):
    with allure.step("Сгенерировать данные нового пользователя"):
        person = Person("en")
        date = Datetime()
        first_name = person.first_name()
        last_name = person.last_name()
        email = person.email()
        phone = person.phone_number()
        date_of_birth = date.formatted_date("%Y-%m-%d")
        password = "aA123456"

    with allure.step("Перейти на сайт"):
        browser.open("/zhenskaya")

    with allure.step("Открыть форму регистрации"):
        browser.element(".sc-ba702bc9-1").click()
        browser.element(by.text("создать")).click()

    with allure.step("Ввести имя нового пользователя"):
        browser.element("input[name='firstName']").click().type(first_name)

    with allure.step("Ввести фамилию нового пользователя"):
        browser.element("input[name='lastName']").click().type(last_name)

    with allure.step("Ввести email нового пользователя"):
        browser.element("input[name='email']").click().type(email)

    with allure.step("Ввести телефон нового пользователя"):
        browser.element("input[name='phone']").click().type(phone)

    with allure.step("Ввести пол нового пользователя"):
        browser.element(by.text("выберите пол")).click()
        browser.element(by.text("женский")).click()

    with allure.step("Ввести дату рождения нового пользователя"):
        browser.element("input[name='birthDate']").click().type(date_of_birth)

    with allure.step("Ввести пароль нового пользователя"):
        browser.execute_script(
            "document.documentElement.getElementsByClassName('sc-7d7c1299-1')[0].scrollIntoView()"
        )
        browser.element("input[name='password']").click().type(password)

    with allure.step("Подтвердить пароль нового пользователя"):
        browser.element("input[name='repeatPassword']").click().type(password)

    with allure.step("Согласиться с условиями"):
        browser.element("label.label").click()

    with allure.step("Отправить форму"):
        browser.element(by.text("создать аккаунт")).click()

    with allure.step("Успешная регистрация. ЛК доступен"):
        browser.element(".sc-ba702bc9-1").click()
        browser.element(by.text("управление аккаунтом")).should(be.present)
