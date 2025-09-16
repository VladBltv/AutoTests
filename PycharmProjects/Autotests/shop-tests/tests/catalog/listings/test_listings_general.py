from befree.api_model import api
import allure
import time
import json
from allure_commons.types import Severity
from requests import Response
from befree.api_model.listings import get_listing_id_and_slug_and_gender


@allure.id("1139")
@allure.title("Вывод в листинг поля Описание (HTML-код)")
@allure.description("Проверяем вывод в листинг поля Описание (HTML-код)")
@allure.tag("API Test")
@allure.severity(Severity.NORMAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_update_content_in_compilation():
    with allure.step(
        "Выбор компиляции, которая не удалена и у которой заполнено поле Описание (HTML-код)"
    ):
        (
            compilation_id,
            compilation_slug,
            compilation_gender,
        ) = get_listing_id_and_slug_and_gender(param="c.content", value="''", condition="<>")

    with allure.step("Отправляем запрос на получение информации о компиляции по приватному апи"):
        response_private_compilation: Response = api.private_session.get(
            url=f"/compilations/{compilation_id}"
        )
    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_compilation.status_code == 200

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получении компиляции по приватному апи"
    ):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step(
        "Проверяем, что поле Описание (HTML-код) совпадает в приватном и публичном апи"
    ):
        assert (
            response_public_compilation.json()["data"]["content"]
            == response_private_compilation.json()["data"]["content"]
        )


@allure.id("1185")
@allure.title("Вывод в листинг поля промо")
@allure.description("Проверяем вывод промо листингов")
@allure.tag("API Test")
@allure.severity(Severity.NORMAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_promo_listings():
    with allure.step(
        "Выбор компиляции,  у которой установлен шаблон листинга - уникальный (промо)"
    ):
        (
            compilation_id,
            compilation_slug,
            compilation_gender,
        ) = get_listing_id_and_slug_and_gender(
            param="c.template", value="'variant2'", condition="="
        )

    with allure.step("Отправляем запрос на получение информации о компиляции по приватному апи"):
        response_private_compilation: Response = api.private_session.get(
            url=f"/compilations/{compilation_id}"
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_compilation.status_code == 200

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получении компиляции по приватному апи"
    ):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Проверяем, что поле template совпадает в приватном и публичном апи"):
        assert (
            response_public_compilation.json()["data"]["template"]
            == response_private_compilation.json()["data"]["template"]
        )


@allure.id("1189")
@allure.title("Вывод товаров в листинг в зависимости от гендера")
@allure.description("Проверяем получение карточек в листинге в  зависимости от гендера")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_gender_in_listings():
    with allure.step("Выбор компиляции, у которой гендер = женский"):
        (
            compilation_id,
            compilation_slug,
            compilation_gender,
        ) = get_listing_id_and_slug_and_gender(param="c.gender", value="'female'", condition="=")

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получении компиляции по гендеру = мужской"
    ):
        listing_data = json.dumps(
            {
                "gender": "male",
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Проверяем, что пришел пусой массив карточек товаров "):
        assert response_public_compilation.json()["data"]["items"] == []


@allure.id("1191")
@allure.title("Скрытые товары не выводятся в листинге")
@allure.description("Проверяем, что в листинге не выводятся скрытые товары")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_with_deletedAt_in_listings():
    with allure.step("Выбор компиляции"):
        (
            compilation_id,
            compilation_slug,
            compilation_gender,
        ) = get_listing_id_and_slug_and_gender(param="c.deleted_at", value="null", condition="is")

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "08c78435-6ed8-4d7f-a7ed-3f73e2fa6359",
                    "goldenRecord": "naro-066844",
                },
                "sort_id": "3",
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Находим первый товар в компиляции"):
        product_id = response_public_compilation.json()["data"]["items"][0]["product_id"]

    with allure.step("Скрываем товар через приватное апи"):
        response_private_delete_product: Response = api.private_session.delete(
            url=f"/products/{product_id}"
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_delete_product.status_code == 200

    time.sleep(15)

    with allure.step("Проверяем, что при повторном запросе листинга не приходит скрытый товар"):
        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

        assert response_public_compilation_2.json()["data"]["items"][0]["product_id"] != product_id


@allure.id("1273")
@allure.title("Скрытые карточки не выводятся в листинге")
@allure.description("Проверяем, что в листинге не выводятся скрытые карточки")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_listing_card_with_deletedAt_in_listings():
    with allure.step("Выбор компиляции"):
        (
            compilation_id,
            compilation_slug,
            compilation_gender,
        ) = get_listing_id_and_slug_and_gender(param="c.deleted_at", value="null", condition="is")

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "08c78435-6ed8-4d7f-a7ed-3f73e2fa6359",
                    "goldenRecord": "naro-066844",
                },
                "sort_id": "3",
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Находим первую карточку товара в компиляции"):
        product_id = response_public_compilation.json()["data"]["items"][0]["product_id"]
        listing_card_id = response_public_compilation.json()["data"]["items"][0]["id"]

    with allure.step("Скрываем товар через приватное апи"):
        response_private_delete_listing_card: Response = api.private_session.delete(
            url=f"/products/{product_id}/cards/{listing_card_id}"
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_delete_listing_card.status_code == 200

    time.sleep(15)

    with allure.step("Проверяем, что при повторном запросе листинга не приходит скрытая карточка"):
        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

        assert response_public_compilation_2.json()["data"]["items"][0]["id"] != listing_card_id


@allure.id("1274")
@allure.title("Каунтер карточек в листинге")
@allure.description("Проверяем, что выводится каунтер товаров в листинге")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_cards_count_in_listings():
    compilation_gender = "female"
    compilation_id = 399
    compilation_slug = "proverka-listinga-so-stikerami"

    with allure.step("Формируем тело запроса и отправляем запрос на получение компиляции "):
        listing_data = {
            "gender": compilation_gender,
            "cityData": {
                "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                "goldenRecord": "sank-823938",
            },
        }

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Проверяем, что в приходит не пустой каунтер цветомоделей"):
        assert response_public_compilation.json()["data"]["cards_count"] == 1


@allure.id("1274")
@allure.title("Каунтер параметров фильтров в листинге")
@allure.description("Проверяем, что выводится каунтер параметров фильтров в листинге")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_cards_count_in_listings():
    compilation_gender = "female"
    compilation_slug = "zen-sale"

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение компиляции с фильтрами"
    ):
        listing_data = json.dumps(
            {
                "gender": "female",
                "cityData": {
                    "fiasId": "08c78435-6ed8-4d7f-a7ed-3f73e2fa6359",
                    "goldenRecord": "naro-066844",
                },
                "filters": {
                    "colors": {"value_ids": [10, 1, 13]},
                    "attributes": [
                        {"attribute_id": 102, "value_ids": [1079, 5, 1093]},
                        {"attribute_id": 187, "value_ids": [11471, 11411]},
                    ],
                    "prices": {"min_value": 300, "max_value": 1499},
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Проверяем, что в приходит не пустой каунтер параметров фильтров"):
        assert response_public_compilation.json()["data"]["filters_count"] == 4
