from befree.api_model import api
import allure
import json
from allure_commons.types import Severity
from requests import Response
from befree.api_model.test_data.listing.sorting_by_price_asc_without_filters import (
    ref_compilation_sorting_by_price_asc_without_filters,
)
from befree.api_model.test_data.listing.sorting_by_price_asc_with_filters import (
    ref_compilation_sorting_by_price_asc_with_filters,
)
from befree.api_model.listings import (
    compare_with_reference,
)


@allure.id("1141")
@allure.title("Cортировка листинга по цене по возрастанию")
@allure.description("Проверяем сортировку по цене по возрастанию")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_sorting_by_price_asc_without_filters():
    compilation_gender = "female"

    id = 397
    compilation_slug = "sortirovka-po-skidke"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "3",
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
            ref_compilation_sorting_by_price_asc_without_filters
        )

    with allure.step(
        "Проверяем, что сортировка по цене по возрастанию корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_sorting_by_price_asc_without_filters,
        )
        assert result, "Сортировка по цене по возрастанию некорректная"


@allure.id("1155")
@allure.title("Cортировка листинга о цене по возрастанию с учетом фильтров")
@allure.description("Проверяем сортировку по цене по возрастанию с учетом фильтров")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_sorting_by_price_asc_with_filters():
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
                "sort_id": "3",
                "filters": {"colors": {"value_ids": [14, 6, 3]}},
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
            ref_compilation_sorting_by_price_asc_with_filters
        )

    with allure.step(
        "Проверяем, что сортировка по цене по возрастанию с фильтрами, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_sorting_by_price_asc_with_filters,
        )

        assert result, "Сортировка по цене по возрастанию с фильтрами некорректная"
