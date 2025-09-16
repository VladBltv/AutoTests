import allure

from befree.api_model.orders.private import OrdersPrivate
from befree.api_model.orders.private.orders.shemas import list_unsent_orders, list_receipts
from allure_commons.types import Severity
from pytest_voluptuous import S


class TestEmployeeDays(OrdersPrivate):
    @allure.id("2696")
    @allure.title("Получение списка зависших заказов")
    @allure.label("service", "Orders")
    @allure.feature("Order")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем получение списка зависших заказов")
    def test_list_unsent_orders(self):
        with allure.step("Запросить список зависших заказов в апи"):
            unsent_orders_response = self.api_orders.list_unsent_orders()
            assert unsent_orders_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(list_unsent_orders) == unsent_orders_response.json()

    @allure.id("2701")
    @allure.title("Получение списка чеков")
    @allure.label("service", "Orders")
    @allure.feature("OFD")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем получение списка чеков")
    def test_list_receipts(self):
        with allure.step("Запросить список чеков в апи"):
            list_receipts_response = self.api_orders.list_receipts()
            assert list_receipts_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(list_receipts) == list_receipts_response.json()
