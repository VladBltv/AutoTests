import allure
from befree.api_model import api
from allure_commons.types import Severity
from requests import Response
from befree.api_model.test_data.product_card.stickers import stickers_list
import befree.api_model.stickers as st
import json


@allure.id("1164")
@allure.title("Вывод одного стикера new, hit, co:create в листинге")
@allure.description("Проверяем установку и удаление одного стикера в листинге")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Стикеры")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_one_sticker():
    compilation_gender = "female"
    # compilation_id = 399
    compilation_slug = "proverka-listinga-so-stikerami"
    products_article = "2321937769"

    with allure.step("Очищаем стикер new у товара"):
        st.edit_with_list_of_articles(stickers_list[0], products_article, "delete")

    with allure.step("Очищаем стикер hit у товара"):
        st.edit_with_list_of_articles(stickers_list[1], products_article, "delete")

    with allure.step("Очищаем кастомный стикер CO:CREATE у товара"):
        st.edit_with_list_of_articles(stickers_list[2], products_article, "delete")

    with allure.step("Добавляем стикер new товару"):
        st.edit_with_list_of_articles(stickers_list[0], products_article, "add")

    with allure.step("Формируем тело запроса и отправляем запрос на получение листинга"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step("Проверяем, что в листинге товар пришел со стикером new"):
        assert (
            response_public_compilation_1.json()["data"]["items"][0]["stickers"][0]["text"] == "new"
        )

    with allure.step("Очищаем стикер new у товара"):
        st.edit_with_list_of_articles(stickers_list[0], products_article, "delete")

    with allure.step("Добавляем стикер hit товару"):
        st.edit_with_list_of_articles(stickers_list[1], products_article, "add")

    with allure.step("Формируем тело запроса и отправляем запрос на получение листинга"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2.status_code == 200

    with allure.step("Проверяем, что в листинге товар пришел со стикером hit"):
        assert (
            response_public_compilation_2.json()["data"]["items"][0]["stickers"][0]["text"] == "hit"
        )

    with allure.step("Очищаем стикер hit у товара"):
        st.edit_with_list_of_articles(stickers_list[1], products_article, "delete")

    with allure.step("Добавляем стикер CO:CREATE  товару"):
        st.edit_with_list_of_articles(stickers_list[2], products_article, "add")

    with allure.step("Формируем тело запроса и отправляем запрос на получение листинга"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation_3: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_3.status_code == 200

    with allure.step("Проверяем, что в листинге товар пришел со стикером CO:CREATE"):
        assert (
            response_public_compilation_3.json()["data"]["items"][0]["stickers"][0]["text"]
            == "CO:CREATE"
        )

    with allure.step("Очищаем стикер CO:CREATE у товара"):
        st.edit_with_list_of_articles(stickers_list[2], products_article, "delete")


@allure.id("1257")
@allure.title("Вывод нескольких стикеров в листинге")
@allure.description("Проверяем установку и удаление нескольких стикеров в листинге")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Стикеры")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_some_stickers():
    compilation_gender = "female"
    compilation_id = 399
    compilation_slug = "proverka-listinga-so-stikerami"
    products_article = "2321937769"

    with allure.step("Очищаем стикер new у товара"):
        st.edit_with_list_of_articles(stickers_list[0], products_article, "delete")

    with allure.step("Очищаем стикер hit у товара"):
        st.edit_with_list_of_articles(stickers_list[1], products_article, "delete")

    with allure.step("Очищаем кастомный стикер CO:CREATE у товара"):
        st.edit_with_list_of_articles(stickers_list[2], products_article, "delete")

    with allure.step("Добавляем стикер new товару"):
        st.edit_with_list_of_articles(stickers_list[0], products_article, "add")

    with allure.step("Добавляем стикер hit товару"):
        st.edit_with_list_of_articles(stickers_list[1], products_article, "add")

    with allure.step("Формируем тело запроса и отправляем запрос на получение листинга"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step("Проверяем, что в листинге товар пришел со стикером new и hit"):
        assert (
            response_public_compilation_1.json()["data"]["items"][0]["stickers"][0]["text"] == "hit"
        )
        assert (
            response_public_compilation_1.json()["data"]["items"][0]["stickers"][1]["text"] == "new"
        )

    with allure.step("Добавляем стикер CO:CREATE  товару"):
        st.edit_with_list_of_articles(stickers_list[2], products_article, "add")

    with allure.step("Формируем тело запроса и отправляем запрос на получение листинга"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2.status_code == 200

    with allure.step("Проверяем, что в листинге товар пришел со стикером hit и CO:CREATE"):
        assert (
            response_public_compilation_2.json()["data"]["items"][0]["stickers"][0]["text"] == "hit"
        )
        assert (
            response_public_compilation_2.json()["data"]["items"][0]["stickers"][1]["text"]
            == "CO:CREATE"
        )
    with allure.step("Очищаем стикер hit у товара"):
        st.edit_with_list_of_articles(stickers_list[1], products_article, "delete")

    with allure.step("Формируем тело запроса и отправляем запрос на получение листинга"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation_3: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_3.status_code == 200

    with allure.step("Проверяем, что в листинге товар пришел со стикером new и CO:CREATE"):
        assert (
            response_public_compilation_3.json()["data"]["items"][0]["stickers"][0]["text"] == "new"
        )
        assert (
            response_public_compilation_3.json()["data"]["items"][0]["stickers"][1]["text"]
            == "CO:CREATE"
        )
