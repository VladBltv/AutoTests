import allure
from allure_commons.types import Severity
from requests import Response

from befree.api_model import api
from befree.api_model.stickers import (
    any_custom_sticker_given,
)
from utils.data_generation import rand_hex, rand_str


@allure.id("1183")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Создание активного стикера")
@allure.description("Проверяем успешное добавление стикера в состоянии активен")
def test_add_sticker_visible():
    with allure.step("Формируем данные для нового стикера"):
        new_sticker_data = {
            "title": rand_str(n=5),
            "front_color_hex": rand_hex(),
            "front_bg_color_hex": rand_hex(),
            "is_visible": 1,
        }

    with allure.step("Отправляем запрос на создание стикера с выбранными данными"):
        response: Response = api.private_session.post(url="/stickers", data=new_sticker_data)

    with allure.step(
        "Проверяем, что ответ успешный и возвращаемые данные совпадают с теми, что были переданы при создании"
    ):
        assert response.status_code == 200
        assert response.json()["data"]["title"] == new_sticker_data["title"]
        assert response.json()["data"]["front_color_hex"] == new_sticker_data["front_color_hex"]
        assert (
            response.json()["data"]["front_bg_color_hex"] == new_sticker_data["front_bg_color_hex"]
        )
        assert response.json()["data"]["is_visible"] is True
        assert response.json()["data"]["products_count"] == 0


@allure.id("1188")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Создание неактивного стикера")
@allure.description("Проверяем успешное добавление стикера в состоянии не активен")
def test_add_sticker_invisible():
    with allure.step("Формируем данные для нового стикера"):
        new_sticker_data = {
            "title": rand_str(n=5),
            "front_color_hex": rand_hex(),
            "front_bg_color_hex": rand_hex(),
            "is_visible": 0,
        }

    with allure.step("Отправляем запрос на создание стикера с выбранными данными"):
        response: Response = api.private_session.post(url="/stickers", data=new_sticker_data)

    with allure.step(
        "Проверяем, что ответ успешный и возвращаемые данные совпадают с теми, что были переданы при создании"
    ):
        assert response.status_code == 200
        assert response.json()["data"]["title"] == new_sticker_data["title"]
        assert response.json()["data"]["front_color_hex"] == new_sticker_data["front_color_hex"]
        assert (
            response.json()["data"]["front_bg_color_hex"] == new_sticker_data["front_bg_color_hex"]
        )
        assert response.json()["data"]["is_visible"] is False
        assert response.json()["data"]["products_count"] == 0


@allure.id("1176")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Нельзя создать стикеры с идентичными заголовками")
@allure.description("Проверяем, что нельзя создать стикер с названием, которое уже есть в базе")
def test_add_sticker_existing():
    with allure.step("Находим в базе существующий кастомный стикер и запоминаем его title"):
        existing_sticker = any_custom_sticker_given()

    with allure.step(
        "Формируем данные для создания нового стикера, в которых используем title существующего стикера"
    ):
        existing_sticker_data = {
            "title": existing_sticker["title"],
            "front_color_hex": existing_sticker["front_color_hex"],
            "front_bg_color_hex": existing_sticker["front_bg_color_hex"],
            "is_visible": 1,
        }

    with allure.step("Отправляем запрос на создание нового стикера"):
        response_post: Response = api.private_session.post(
            url="/stickers", data=existing_sticker_data
        )

    with allure.step(
        "Проверяем, что запрос отадет ошибку и второй стикер с таким title не создается"
    ):
        assert response_post.status_code == 422
        assert response_post.json()["errors"][0]["data"]["title"][0].find("уже существует") != -1
