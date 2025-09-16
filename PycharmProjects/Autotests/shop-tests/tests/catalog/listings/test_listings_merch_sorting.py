from befree.api_model import api
import allure
import json
import time
from allure_commons.types import Severity
from requests import Response
from befree.api_model.test_data.listing.with_merch import (
    ref_compilation_with_merch_1,
    ref_compilation_with_merch_2,
)
from befree.api_model.test_data.listing.add_and_delete_merch import (
    ref_compilation_without_merch,
    ref_compilation_with_add_merch,
)
from befree.api_model.test_data.listing.with_merch_and_filters import (
    ref_compilation_without_merch_with_filters,
    ref_compilation_with_merch_and_filters,
)
from befree.api_model.listings import (
    compare_with_reference,
)
from befree.api_model.test_data.listing.without_merch_default import (
    ref_compilation_without_merch_default,
)


@allure.id("1157")
@allure.title("Сортировка по популярности + мерч в листинге")
@allure.description("Проверяем сортировку по популярности, если заполнен мерч")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_merch():
    compilation_gender = "female"
    compilation_id = 394
    compilation_slug = "sortirovka-po-populiarnosti-s-mercom"

    with allure.step("Изменяем мерч"):
        merch_data = json.dumps(
            {
                "items": [
                    {"card_id": 18609, "sort_order": 0},
                    {"card_id": 155056, "sort_order": 1},
                ]
            }
        )

        response_private_put_merch_1: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}/merch",
            data=merch_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_put_merch_1.status_code == 200

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
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
        "Проверяем, что количество item'сов совпадает с количеством элементов в эталонной структкуре"
    ):
        assert len(response_public_compilation_1.json()["data"]["items"]) == len(
            ref_compilation_with_merch_1
        )

    with allure.step("Проверяем, что сортировка с мерчом корректная, совпадает с эталоном"):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_with_merch_1,
        )

        assert result, "Сортировка с мерчом некорректная"

    with allure.step("Изменяем мерч"):
        merch_data = json.dumps(
            {
                "items": [
                    {"card_id": 18609, "sort_order": 0},
                    {"card_id": 155056, "sort_order": 1},
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

    with allure.step("Формируем тело запроса и отправляем заново запрос на получении компиляции"):
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

        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2.status_code == 200

    with allure.step(
        "Проверяем, что сортировка после изменения мерча корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_2.json()["data"]["items"],
            ref_compilation_with_merch_2,
        )

        assert result, "Сортировка после изменения мерча некорректная"


@allure.id("1156")
@allure.title("Сортировка по популярности + добавление/удаление мерча в листинге")
@allure.description("Проверяем сортировку по популярности при добавлении и удалении мерча")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_add_and_delete_merch():
    compilation_gender = "female"
    compilation_id = 395
    compilation_slug = "sortirovka-po-populiarnosti-s-mercom1"

    with allure.step("Убираем мерч в компиляции"):
        merch_data = json.dumps({"items": []})

        response_private_put_merch_1: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}/merch",
            data=merch_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_put_merch_1.status_code == 200

    time.sleep(15)

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получениие компиляции без мерча"
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

    with allure.step("Проверяем, что сортировка без мерча корректная, совпадает с эталоном"):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_without_merch,
        )

        assert result, "Сортировка без мерча некорректная"

    with allure.step("Добавляем мерч в компиляции"):
        merch_data = json.dumps(
            {
                "items": [
                    {"card_id": 155056, "sort_order": 0},
                    {"card_id": 18609, "sort_order": 1},
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

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получениие компиляции с добавленным мерчом"
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

        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2.status_code == 200

    with allure.step("Проверяем, что сортировка с мерчом корректная, совпадает с эталоном"):
        result = compare_with_reference(
            response_public_compilation_2.json()["data"]["items"],
            ref_compilation_with_add_merch,
        )

        assert result, "Сортировка с мерчом некорректная"


@allure.id("1154")
@allure.title("Сортировка по популярности с фильтрами")
@allure.description("Проверяем сортировку по популярности с фильтрами")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_merch_and_filters():
    compilation_gender = "female"
    compilation_id = 396
    compilation_slug = "sortirovka-po-populiarnosti-s-mercom-i-filtrami"

    with allure.step("Убираем мерч в компиляции"):
        merch_data = json.dumps({"items": []})

        response_private_put_merch_1: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}/merch",
            data=merch_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_private_put_merch_1.status_code == 200

    time.sleep(15)

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получениие компиляции без мерча с фильтрами"
    ):
        listing_data = json.dumps(
            {
                "gender": compilation_gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "sort_id": "1",
                "filters": {
                    "colors": {"value_ids": [10, 1]},
                    "prices": {"min_value": 350, "max_value": 1199},
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
        "Проверяем, что сортировка без мерча с примененными фильтрами корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_without_merch_with_filters,
        )

        assert result, "Сортировка без мерча с примененными фильтрами некорректная"

    with allure.step("Добавляем мерч в компиляции"):
        merch_data = json.dumps(
            {
                "items": [
                    {"card_id": 18609, "sort_order": 0},
                    {"card_id": 85689, "sort_order": 1},
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

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получениие компиляции с мерчом и фильтрами"
    ):
        listing_data = json.dumps(
            {
                "gender": "female",
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
                "filters": {
                    "colors": {"value_ids": [8, 1]},
                    "prices": {"min_value": 300, "max_value": 1199},
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

    with allure.step(
        "Проверяем, что сортировка c мерчом и примененными фильтрами корректная, совпадает с эталоном"
    ):
        result = compare_with_reference(
            response_public_compilation_2.json()["data"]["items"],
            ref_compilation_with_merch_and_filters,
        )

        assert result, "Сортировка c мерчом и примененными фильтрами некорректная"


@allure.id("1252")
@allure.title("Сортировка по популярности без мерча (по умолчанию)и")
@allure.description("Проверяем сортировку по популярности без мерча (по умолчанию)")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_without_merch_default():
    compilation_gender = "female"
    compilation_id = 400
    compilation_slug = "sortirovka-po-populiarnosti-bez-merca"

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получениие компиляции без мерча"
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

    with allure.step("Проверяем, что сортировка без мерча корректная, совпадает с эталоном"):
        result = compare_with_reference(
            response_public_compilation_1.json()["data"]["items"],
            ref_compilation_without_merch_default,
        )

        assert result, "Сортировка без мерча с сортировкой по умолчанию некорректная"
