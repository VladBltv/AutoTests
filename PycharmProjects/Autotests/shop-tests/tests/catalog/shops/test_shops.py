import allure
from allure_commons.types import Severity
from requests import Response
from befree.api_model import api


@allure.id("1199")
@allure.title("Список магазинов в админке")
@allure.description("Проверяем получение списка магазинов")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.label("layers", "api")
def test_get_shops_list():
    with allure.step("Отправляем запрос на список магазинов"):
        response_get: Response = api.private_session.get(url="/stores")

    with allure.step("Проверяем, что ответ успешный"):
        assert response_get.status_code == 200


@allure.id("1197")
@allure.title("Изменение данных магазина в админке")
@allure.description("Проверяем изменение данных магазина")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.label("layers", "api")
def test_edit_shops():
    with allure.step("Находим активный магазин"):
        ...
