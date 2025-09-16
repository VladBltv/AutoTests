import allure
from allure_commons.types import Severity
from requests import Response
from befree.api_model import api

from befree.api_model.stickers import (
    sticker_with_products_given,
    get_products_by_sticker_id,
)


@allure.id("1177")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Выгрузка списка товаров, привязанных к стикеру")
@allure.description("Проверяем выгрузку товаров, привязанных к стикеру")
def test_get_product_list_by_sticker_id():
    with allure.step("Находим стикер, в котором привязаны продукты"):
        sticker = sticker_with_products_given()

    with allure.step("Находим товары, к которым привязан стикер"):
        products = get_products_by_sticker_id(sticker["id"])
        articles = [i["article"] for i in products]

    with allure.step("Запускаем выгрузку товаров по стикеру"):
        response_get: Response = api.private_session.get(
            url=f"/stickers/product_articles/{sticker['id']}"
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_get.status_code == 200

    with allure.step("Сверяем полученный список продуктов со списком из базы"):
        response_text = response_get.text
        articles_loaded = response_text.split("\n")
        assert articles_loaded.sort() == articles.sort()
