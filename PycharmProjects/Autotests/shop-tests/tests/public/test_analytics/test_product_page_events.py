import allure
from allure_commons.types import Severity
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders.public import OrdersPublic
from utils import helpers
import re


class TestProductPageEvents:
    @allure.title("Событие клика на блок Состав и параметры")
    @allure.label("microservice", "Public")
    @allure.feature("Yandex")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.description(
        """При каждом клике на блок с информацией о составе и параметрах в яндекс метрику отправляется событие 'Product Card Click Parameters', {section: 'Qualities'}"""
    )
    def test_product_click_qualities(self, shop_page):
        with allure.step("Перейти на страницу товара"):
            shop_page.goto("/zhenskaya/product/SLIMRIB/1")

        with allure.step(
            "Кликнуть на блок Состав и параметры первый раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("состав и параметры").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Qualities'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Qualities%22%7D" in url

        with allure.step(
            "Кликнуть на блок Состав и параметры второй раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("состав и параметры").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Qualities'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Qualities%22%7D" in url

    @allure.title("Событие клика на блок Описание товара")
    @allure.label("microservice", "Public")
    @allure.feature("Yandex")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.description(
        """При каждом клике на блок Описание товара в яндекс метрику отправляется событие 'Product Card Click Parameters', {section: 'Description'}"""
    )
    def test_product_click_description(self, shop_page):
        with allure.step("Перейти на страницу товара"):
            shop_page.goto("/zhenskaya/product/SLIMRIB/1")

        with allure.step(
            "Кликнуть на блок Описание товара первый раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("описание товара").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Description'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Description%22%7D" in url

        with allure.step(
            "Кликнуть на блок Описание товара второй раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("описание товара").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Description'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Description%22%7D" in url

    @allure.title("Событие клика на блок Рекомендации по уходу")
    @allure.label("microservice", "Public")
    @allure.feature("Yandex")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.description(
        """При каждом клике на блок Рекомендации по уходу в яндекс метрику отправляется событие 'Product Card Click Parameters', {section: 'Recommendations For Care]'}"""
    )
    def test_product_click_recommendations_for_care(self, shop_page):
        with allure.step("Перейти на страницу товара"):
            shop_page.goto("/zhenskaya/product/SLIMRIB/1")

        with allure.step(
            "Кликнуть на блок Рекомендации по уходу первый раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("рекомендации по уходу").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Recommendations For Care'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Recommendations%20For%20Care%22%7D" in url

        with allure.step(
            "Кликнуть на блок Рекомендации по уходу второй раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("рекомендации по уходу").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Recommendations For Care'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Recommendations%20For%20Care%22%7D" in url

    @allure.title("Событие клика на блок Доставка и оплата")
    @allure.label("microservice", "Public")
    @allure.feature("Yandex")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.description(
        """При каждом клике на блок Доставка и оплата в яндекс метрику отправляется событие 'Product Card Click Parameters', {section: 'Delivery And Payment]'}"""
    )
    def test_product_click_delivery_and_payments(self, shop_page):
        with allure.step("Перейти на страницу товара"):
            shop_page.goto("/zhenskaya/product/SLIMRIB/1")

        with allure.step(
            "Кликнуть на блок Доставка и оплата первый раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("Доставка и оплата").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Delivery And Payment'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Delivery%20And%20Payment%22%7" in url

        with allure.step(
            "Кликнуть на блок Доставка и оплата второй раз и перехватить запрос с гет параметром Product Card Click Parameters"
        ):
            with shop_page.expect_request(
                re.compile(
                    r"https://mc\.yandex\.ru/watch/55153801/1\?page-url=goal%3A%2F%2Fshop-fe-qa01\.befree.ru%2FProduct%20Card%20Click%20Parameters.*"
                )
            ) as request_info:
                shop_page.get_by_text("Доставка и оплата").click()

        with allure.step(
            "Проверить, что в урле передается {section: 'Delivery And Payment'} -  значение таба по которому был клик "
        ):
            url = request_info.value.url

            assert "site-info=%7B%22section%22%3A%22Delivery%20And%20Payment%22%7D" in url
