import allure
import json
from befree.api_model import api
from allure_commons.types import Severity
from requests import Response
from befree.api_model.listings import (
    compare_with_reference,
)
from befree.api_model.test_data.listing.with_sticker_new import (
    ref_compilation_with_sticker_new,
)
from befree.api_model.test_data.listing.without_new_default import (
    ref_compilation_without_new_default,
)


@allure.id("1152")
@allure.title("Сортировка по новинкам, если у всех товаров установлен стикер new")
@allure.description("Проверяем сортировку по новинкам, если у всех товаров установлен стикер new")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_sticker_new():
    compilation_gender = "female"
    # compilation_id = 398
    compilation_slug = "sortirovka-po-novinkam"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "2",
            }
        )

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step(
        "Проверяем, что количество item'сов совпадает с количеством элементов в эталонной структкуре"
    ):
        assert len(response_public_compilation_1.json()["data"]["items"]) == len(
            ref_compilation_with_sticker_new
        )

    with allure.step("Проверяем, что сортировка со стикером new корректная, совпадает с эталоном"):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_with_sticker_new,
        )

        assert result, "Сортировка со стикером new некорректная"


@allure.id("1251")
@allure.title("Сортировка по новинкам без товаров со стикером new (по умолчанию)")
@allure.description("Проверяем сортировку по новинкам без товаров со стикером new (по умолчанию)")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_without_new_default():
    compilation_gender = "female"
    # compilation_id = 401
    compilation_slug = "sortirovka-po-novinkam-po-umolcaniiu"

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получениие компиляции по товарам без стикера new"
    ):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "1",
            }
        )

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step(
        "Проверяем, что сортировка товаров без стикера нью (по умолчанию) корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_without_new_default,
        )

        assert result, "Сортировка без стикера new с сортировкой по умолчанию некорректная"
