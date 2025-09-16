import allure
from allure_commons.types import Severity
from requests import Response

from befree.api_model import api, db_connection


@allure.id("1202")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Список стикеров")
@allure.description("Проверяем успешное получение списка стикеров")
def test_get_stickers_list():
    with allure.step("Отправить запрос на получение списка стикеров"):
        response: Response = api.private_session.get(url="/stickers")

    with allure.step("Считаем общее количество стикеров, полученных через API"):
        stickers_total_api = len(response.json()["data"])

    with allure.step("Получаем список стикеров из базы"):
        stickers_list_query = """
            select ps.id , ps.is_visible 
            from product_stickers ps 
        """

        stickers_list_db = db_connection.catalog.get_data(stickers_list_query)

    with allure.step("Считаем количество стикеров в базе"):
        stickers_total_db = len(stickers_list_db)

    with allure.step("Проверяем, что ответ успешный"):
        assert response.status_code == 200

    with allure.step(
        "Проверяем, что количество стикеров, полученных через АПИ равно количеству стикеров в базе"
    ):
        assert stickers_total_api == stickers_total_db


@allure.id("1180")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Получение статуса активности стикера")
@allure.description("Проверяем, что АПИ отдает статус активности стикеров")
def test_stickers_visibility():
    with allure.step("Отправить запрос на получение списка стикеров"):
        response: Response = api.private_session.get(url="/stickers")

    with allure.step("Считаем количество активных стикеров, полученных через API"):
        stickers_active_api = len(
            list(filter(lambda item: item["is_visible"] is True, response.json()["data"]))
        )

    with allure.step("Считаем количество не активных стикеров, полученных через API"):
        stickers_inactive_api = len(
            list(filter(lambda item: item["is_visible"] is False, response.json()["data"]))
        )

    with allure.step("Получаем список стикеров из базы"):
        stickers_list_query = """
            select ps.id , ps.is_visible 
            from product_stickers ps 
        """

        stickers_list_db = db_connection.catalog.get_data(stickers_list_query)

    with allure.step("Считаем количество активных стикеров, полученных из базы"):
        stickers_active_db = len(
            list(filter(lambda item: item["is_visible"] is True, stickers_list_db))
        )

    with allure.step("Считаем количество не активных стикеров, полученных из базы"):
        stickers_inactive_db = len(
            list(filter(lambda item: item["is_visible"] is False, stickers_list_db))
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response.status_code == 200

    with allure.step(
        "Проверяем, что количество активных стикеров, полученных через АПИ равно количеству активных стикеров в базе"
    ):
        assert stickers_active_api == stickers_active_db

    with allure.step(
        "Проверяем, что количество не активных стикеров, полученных через АПИ равно количеству не активных стикеров в базе"
    ):
        assert stickers_inactive_api == stickers_inactive_db


@allure.id("1198")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Сортировка списка стикеров в админке")
@allure.description("Проверяем, что неактивные стикеры идут после активных")
def test_stickers_sorting():
    ...
