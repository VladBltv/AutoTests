import allure
from allure_commons.types import Severity
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders.public import OrdersPublic
from utils import helpers
from mimesis import Person
import re


class TestRegistrationEvents:
    @allure.title("Событие регистрации с главной страницы с выбранной галкой подписки")
    @allure.label("microservice", "Public")
    @allure.feature("Yandex")
    @allure.feature("Регистрация пользователя")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        """При регистрации пользователя с главной страницы, если он установил галку подписки отправляется событие 'Email-Subscribe', {from: 'Main'}"""
    )
    def test_register_from_main_with_subscription(self, shop_page):
        shop_page.goto(url="/zhenskaya")
        shop_page.locator(".sc-a9b09bfd-0 > .sc-2b366990-0").click()
        shop_page.get_by_text("создать").click()
        shop_page.locator("#firstName").click()
        shop_page.locator("#firstName").fill(Person().first_name())
        shop_page.locator("#lastName").click()
        shop_page.locator("#lastName").fill(Person().last_name())
        shop_page.locator("#email").click()
        shop_page.locator("#email").fill(Person().email())
        shop_page.locator("#phone").click()
        shop_page.locator("#phone").fill("+7 (123) 456-78-90")
        shop_page.get_by_test_id("signup-form-input-gender").click()
        shop_page.get_by_test_id("signup-form-input-gender").get_by_text("женский").click()
        shop_page.get_by_test_id("signup-form-input-birthDate").get_by_role("textbox").click()
        shop_page.get_by_test_id("signup-form-input-birthDate").get_by_role("textbox").fill("2000-10-10")
        shop_page.locator("#password").click()
        shop_page.locator("#password").fill("aA123456")
        shop_page.locator("#repeatPassword").click()
        shop_page.locator("#repeatPassword").fill("aA123456")
        shop_page.locator("label").filter(
            has_text="Подписаться на рассылку, чтобы получать секретные скидки и предложения. Подписыв"
        ).locator("div").first.click()

        with allure.step(
            "Кликнуть на кнопку отправки формы и отловить запрос с гет параметром Registration-submit"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2F.*\.befree.ru%2FRegistration-submit.*"
                )
            ) as request_info:
                shop_page.get_by_test_id("signup-form-button-submit").click()

        with allure.step(
            "Проверить, что в урле передается {from: 'Main'} -  значение страницы, с которой была регистрация"
        ):
            url = request_info.value.url

            assert "site-info=%7B%22from%22%3A%22Main%22%7D" in url
