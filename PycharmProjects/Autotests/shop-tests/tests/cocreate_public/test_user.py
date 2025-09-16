import allure
import time
from allure_commons.types import Severity
from selene.support import by
from selene.support.shared import browser
from selene import have, be
from mimesis import Person, Datetime
from selenium.webdriver.common.keys import Keys
from utils.database import filling_out_table
from befree.api_model.cocreate.private import CocreatePrivate


class TestUser(CocreatePrivate):
    @allure.id("2685")
    @allure.title("Успешная авторизация существующего пользователя")
    @allure.description("Проверяем, что пользователь успешно авторизуется")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.label("feature", "Авторизация, регистрация и восстановление пароля")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Cocreate Public")
    @allure.label("layers", "ui")
    def test_successful_auth(self, cocreate_browser_config):
        with allure.step("Перейти на сайт"):
            browser.open("")

        with allure.step("Открыть форму авторизации"):
            browser.element(by.text("войти")).click()
            browser.element(by.text("Вход в befree community")).should(be.present)

        with allure.step("Ввести email существующего пользователя"):
            browser.element("input[type='email']").click().type("melon.test.2@yandex.ru")

        with allure.step("Ввести пароль существующего пользователя"):
            browser.element("input[type='password']").click().type("aA123456")

        with allure.step("Отправить форму"):
            browser.element("input[type='password']").send_keys(Keys.ENTER)
            time.sleep(5)

        with allure.step("Успешная авторизация. ЛК доступен"):
            browser.element(by.text("профиль")).click()
            browser.element(by.text("добавить работу")).should(be.present)

    @allure.id("2688")
    @allure.title("Успешная регистрация существующего пользователя")
    @allure.description("Проверяем, что пользователь успешно регистрируется")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.label("feature", "Авторизация, регистрация и восстановление пароля")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Cocreate Public")
    @allure.label("layers", "ui")
    def test_successful_registration(self, cocreate_browser_config):
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
            browser.open("")

        with allure.step("Открыть форму регистрации"):
            browser.element(by.text("войти")).click()
            browser.element(by.text("Создать аккаунт")).click()
            browser.element(by.partial_text("Регистрация")).should(be.present)

        with allure.step("Ввести имя нового пользователя"):
            browser.element("input[name='firstName']").click().type(first_name)

        with allure.step("Ввести фамилию нового пользователя"):
            browser.element("input[name='lastName']").click().type(last_name)

        with allure.step("Ввести email нового пользователя"):
            browser.element("input[name='email']").click().type(email)

        with allure.step("Ввести телефон нового пользователя"):
            browser.element("input[name='phone']").click().type(phone)

        with allure.step("Ввести дату рождения нового пользователя"):
            browser.element("input[name='birthdayAt']").click().type(date_of_birth)

        with allure.step("Ввести пол нового пользователя"):
            browser.element("input[name='gender']").click()
            browser.element(by.text("женский")).click()

        with allure.step("Ввести пароль нового пользователя"):
            browser.element("input[name='password']").click().type(password)

        with allure.step("Подтвердить пароль нового пользователя"):
            browser.element("input[name='passwordConfirmation']").click().type(password)

        with allure.step("Отправить форму"):
            browser.element(by.text("создать аккаунт")).click()
            time.sleep(5)

        with allure.step("Успешная регистрация. ЛК доступен"):
            browser.element(by.text("профиль")).click()
            browser.element(by.text("выйти из аккаунта")).should(be.present)

    @allure.id("2684")
    @allure.title("При попытке лайкнуть появляется попап авторизации")
    @allure.description("Проверяем, что неавторизованный пользователь не может лайкать работы")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.label("feature", "Авторизация, регистрация и восстановление пароля")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Cocreate Public")
    @allure.label("layers", "ui")
    def test_non_auth_like(self, cocreate_browser_config):
        with allure.step("Перейти на сайт"):
            browser.open("")

        with allure.step("На главной странице кликнуть на сердечко"):
            browser.element("button[class*='sc-3dd7a639']").click()

            with allure.step("Появляется попап авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.present)

            with allure.step("Закрываем попап"):
                browser.element("button[class*='sc-cd4d0d1d-0 fLGVhj sc-ee07101c-2']").click()

        with allure.step("В галерее работ кликнуть на сердечко"):
            browser.element(by.text("креаторы")).click()
            browser.element("button[class*='sc-3dd7a639']").click()

            with allure.step("Появляется попап авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.present)

            with allure.step("Закрываем попап"):
                browser.element("button[class*='sc-cd4d0d1d-0 fLGVhj sc-ee07101c-2']").click()

        with allure.step("Открываем страницу работы"):
            browser.element("div[class*='sc-1d6cce6d-0']").click()
            browser.element(by.text("поделиться:")).should(be.present)

        with allure.step("Лайкаем работу"):
            browser.element("/html/body/main/div[2]/div[3]/div[1]/div[2]/button").click()

            with allure.step("Появляется попап авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.present)

            with allure.step("Закрываем попап"):
                browser.element("button[class*='sc-cd4d0d1d-0 fLGVhj sc-ee07101c-2']").click()

    @allure.id("2683")
    @allure.title("Форма авторизации на странице конкурса")
    @allure.description("Проверяем, что неавторизованный пользователь не может лайкать работы")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.label("feature", "Авторизация, регистрация и восстановление пароля")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Cocreate Public")
    @allure.label("layers", "ui")
    def test_auth_in_contest(self, cocreate_browser_config):
        with allure.step("Создаем конкурс"):
            create_contest_response = self.api_contests.create()
            assert create_contest_response.status_code == 201
            contest_slug = create_contest_response.json()["data"]["slug"]

        with allure.step("Открываем страницу конкурса"):
            browser.open(f"/contests/{contest_slug}")

        with allure.step("Проверяем, что конкурс не выводится"):
            browser.element(by.text("Страница не найдена")).should(be.present)

        with allure.step("Изменяем статус конкурса на 'start'"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("start", create_contest_response.json()["data"]["id"])],
            }

            filling_out_table(data=data, service="cocreate")

        with allure.step("Открываем страницу конкурса"):
            browser.open(f"/contests/{contest_slug}")

            with allure.step("Нажать Принять участие под неавторизованным пользователем"):
                browser.element(by.text("принять участие в конкурсе")).click()

            with allure.step("Проверяем, что показывается форма для авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.present)

        with allure.step("Изменяем статус конкурса на 'voting'"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("voting", create_contest_response.json()["data"]["id"])],
            }
            filling_out_table(data=data, service="cocreate")

        with allure.step("Открываем страницу конкурса"):
            browser.open(f"/contests/{contest_slug}")

            with allure.step("Нажать Принять участие под неавторизованным пользователем"):
                browser.element(by.text("принять участие в конкурсе")).click()

            with allure.step("Проверяем, что показывается форма для авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.present)

        with allure.step("Изменяем статус конкурса на 'voting'"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("counting", create_contest_response.json()["data"]["id"])],
            }
            filling_out_table(data=data, service="cocreate")

        with allure.step("Открываем страницу конкурса"):
            browser.open(f"/contests/{contest_slug}")

            with allure.step("Проверяем, что не показывается форма для авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.disabled)

        with allure.step("Изменяем статус конкурса на 'voting'"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("archived", create_contest_response.json()["data"]["id"])],
            }
            filling_out_table(data=data, service="cocreate")

        with allure.step("Открываем страницу конкурса"):
            browser.open(f"/contests/{contest_slug}")

            with allure.step("Проверяем, что не показывается форма для авторизации"):
                browser.element(by.text("Вход в befree community")).should(be.disabled)
