import allure

from befree.api_model.orders.private import OrdersPrivate
from befree.api_model.orders.db_queries.queries import QueriesOrders
from befree.api_model.orders.private.employee_days.shemas import employee_days_list
from allure_commons.types import Severity
from pytest_voluptuous import S
from datetime import datetime, timedelta


class TestEmployeeDays(OrdersPrivate, QueriesOrders):
    @allure.id("2699")
    @allure.title("Получение списка дней сотрудников")
    @allure.label("service", "Orders")
    @allure.feature("MyCard")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем получение списка дней сотрудников")
    def test_list_employee_days(self):
        with allure.step("Запросить список дней сотрудников в апи"):
            employee_days_list_response = self.api_employee_days.get_employee_days()
            assert employee_days_list_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(employee_days_list) == employee_days_list_response.json()

        with allure.step("Запросить список дней сотрудников в бд"):
            employee_days_list_db = self.list_employee_days()

        with allure.step("Сравниваем количество активных дней сотрудников"):
            assert len(employee_days_list_response.json()["data"]["employeeDays"]) == len(
                employee_days_list_db
            )

    @allure.id("2698")
    @allure.title("Создание дня сотрудника")
    @allure.label("service", "Orders")
    @allure.feature("MyCard")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем создание дня сотрудника")
    def test_create_employee_days(self):
        with allure.step("Получаем список дней сотрудников в апи"):
            employee_days_list_response = self.api_employee_days.get_employee_days()

        with allure.step("Выбираем следующий день от последнего дня сотрудника"):
            date_from_response = employee_days_list_response.json()["data"]["employeeDays"][0][
                "date"
            ]
            date_for_create = (
                datetime.strptime(date_from_response, "%d/%m/%Y") + timedelta(days=1)
            ).strftime("%d.%m.%Y")

        with allure.step("Отправляем запрос на создание дня сотрудника"):
            create_employee_day_response = self.api_employee_days.create_employee_day(
                date=date_for_create
            )
            assert create_employee_day_response.status_code == 204

    @allure.id("2697")
    @allure.title("Удаление дня сотрудника")
    @allure.label("service", "Orders")
    @allure.feature("MyCard")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем удаление дня сотрудника")
    def test_delete_employee_days(self):
        with allure.step("Запрашиваем список дней сотрудников в апи"):
            employee_days_list_response = self.api_employee_days.get_employee_days()
            assert employee_days_list_response.status_code == 200

        with allure.step("Отправляем запрос на удаление дня сотрудника"):
            id_employee_day = employee_days_list_response.json()["data"]["employeeDays"][0]["id"]
            delete_employee_day_response = self.api_employee_days.delete_employee_day(
                id=id_employee_day
            )
            assert delete_employee_day_response.status_code == 204
