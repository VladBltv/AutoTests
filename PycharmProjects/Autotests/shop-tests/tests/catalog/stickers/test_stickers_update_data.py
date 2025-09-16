import allure
from allure_commons.types import Severity
from requests import Response

from befree.api_model import api
from befree.api_model.stickers import (
    get_sticker_by_id_via_api,
    any_custom_sticker_given,
)
from utils.data_generation import rand_str, rand_hex


@allure.id("1187")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Обновление данных в стикере")
@allure.description("Проверяем успешное обновление данных в стикере")
def test_update_sticker_data():
    with allure.step("Найти в базе кастомный стикер и записать его данные"):
        custom_sticker = any_custom_sticker_given()

    with allure.step("Отправить в выбранный стикер новые данные"):
        new_data_for_sticker = {
            "title": rand_str(n=5),
            "front_color_hex": rand_hex(),
            "front_bg_color_hex": rand_hex(),
            "is_visible": "1",
            "product_action_flag": "add",
            "_method": "PUT",
        }

        response: Response = api.private_session.post(
            url=f"/stickers/{custom_sticker['id']}", data=new_data_for_sticker
        )

    with allure.step("Проверить, что метод отдал успешный ответ"):
        assert response.status_code == 200

    with allure.step("Проверить, что новые данные записались в изменяемый стикер"):
        response_data = get_sticker_by_id_via_api(custom_sticker["id"])

        assert response_data["data"]["title"] == new_data_for_sticker["title"]
        assert response_data["data"]["front_color_hex"] == new_data_for_sticker["front_color_hex"]
        assert (
            response_data["data"]["front_bg_color_hex"]
            == new_data_for_sticker["front_bg_color_hex"]
        )
