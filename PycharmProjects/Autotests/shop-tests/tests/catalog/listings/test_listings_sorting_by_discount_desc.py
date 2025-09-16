from befree.api_model import api
import allure
import json
import time
from allure_commons.types import Severity
from requests import Response
from befree.api_model.test_data.listing.sorting_by_discount import (
    ref_compilation,
)
from befree.api_model.test_data.listing.sorting_by_discount_with_filters import (
    ref_compilation_sorting_by_discount_with_filters,
)
from befree.api_model.listings import (
    compare_with_reference,
)


@allure.id("1186")
@allure.title("Сортировка по скидке")
@allure.description("Проверяем сортировку по скидке")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_sorting_by_discount():
    compilation_gender = "female"
    compilation_id = 397
    compilation_slug = "sortirovka-po-skidke"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "5",
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
        assert len(response_public_compilation_1.json()["data"]["items"]) == len(ref_compilation)

    with allure.step("Проверяем, что сортировка по убыванию цены корректная, совпадает с эталоном"):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation,
        )

        assert result, "Сортировка по убыванию цены некорректная"

    with allure.step("Добавляем мерч, чтобы посмотреть что сортировка не изменится"):
        merch_data = json.dumps(
            {
                "items": [
                    {"card_id": 248958, "sort_order": 0},
                    {"card_id": 248960, "sort_order": 1},
                ]
            }
        )

        response_private_put_merch_2: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}/merch",
            data=merch_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_put_merch_2.status_code == 200

    time.sleep(15)

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "5",
            }
        )

        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2.status_code == 200

    with allure.step(
        "Проверяем, что количество item'сов совпадает с количеством элементов в эталонной структкуре"
    ):
        assert len(response_public_compilation_2.json()["data"]["items"]) == len(ref_compilation)

    with allure.step(
        "Проверяем, что сортировка с мерчом и сортировкой по скидке корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_2.json()["data"]["items"],
            ref_compilation,
        )

        assert result, "Сортировка с мерчом и сортировкой по скидке некорректная"


@allure.id("1186")
@allure.title("Сортировка по скидке с фильтрами")
@allure.description("Проверяем сортировку по скидке с фильтрами")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_sorting_by_discount_with_filters():
    compilation_gender = "female"
    # compilation_id = 397
    compilation_slug = "sortirovka-po-skidke"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "5",
                "filters": {
                    "colors": {"value_ids": [1, 7, 3, 6]},
                    "prices": {"min_value": 350, "max_value": 1599},
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

    with allure.step(
        "Проверяем, что количество item'сов совпадает с количеством элементов в эталонной структкуре"
    ):
        assert len(response_public_compilation_1.json()["data"]["items"]) == len(
            ref_compilation_sorting_by_discount_with_filters
        )

    with allure.step(
        "Проверяем, что сортировка по скидке и с фильтрами корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_sorting_by_discount_with_filters,
        )

        assert result, "Сортировка по скидке и с фильтрами  некорректная"
