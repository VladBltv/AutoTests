import allure
from befree.api_model import api
from allure_commons.types import Severity
from requests import Response
from befree.api_model.test_data.product_card import compilations as cp
import befree.api_model.product as pc


@allure.title("Атрибуты, установленные в категории")
@allure.description("Проверить, что в апи приходят атрибуты, установленные в категории")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_attributes():
    kladr = "7800000000000"
    compilation_id = 113
    product_article = "2311012712"

    with allure.step("Отправляем запрос на очищение всех атрибуты в категории"):
        response_private_put_compilation: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}",
            data=cp.compilation_without_attributes,
            headers={"Content-Type": "application/json"},
        )
    with allure.step("Проверяем, что запрос на изменение категории прошел успешно"):
        assert response_private_put_compilation.status_code == 200

    with allure.step("Отправляем запрос на получение товара этой категории"):
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что пришел пустой массив с атрибутами"):
        assert product_api["variations"][0]["attributes"] == []

    with allure.step("Отправляем запрос на добавление атрибутов в категории"):
        response_private_put_compilation: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}",
            data=cp.compilation_with_attributes,
            headers={"Content-Type": "application/json"},
        )
    with allure.step("Проверяем, что запрос на изменение категории прошел успешно"):
        assert response_private_put_compilation.status_code == 200

    with allure.step("Отправляем запрос на получение товара этой категории"):
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что атрибуты пришли те, что мы указали в категории"):
        assert product_api["variations"][0]["attributes"] == cp.ref_attributes
