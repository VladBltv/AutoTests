from befree.api_model import api
import allure
import json
from allure_commons.types import Severity
from requests import Response
from befree.api_model.listings import compare_sub_menu_with_reference
from befree.api_model.test_data.listing.sub_categories import (
    ref_compilation_sub_menu,
)
from befree.api_model.test_data.listing.sub_menu_sorting_change import (
    ref_compilation_sub_menu_before_sorting,
    ref_compilation_sub_menu_after_sorting,
)
from befree.api_model.test_data.listing.hidden_subcategory_in_sub_menu import (
    ref_compilation_sub_menu_before_hiding,
    ref_compilation_sub_menu_after_hiding,
)


@allure.id("1258")
@allure.title("Листинга без субкатегорий")
@allure.description("Проверяем получение пустого массива sub_menu в листинге")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_without_sub_menu():
    compilation_gender = "female"
    compilation_slug_podborka = "zen-novinki"
    compilation_slug_category = "bosonozki-zenskie"

    with allure.step("Формируем тело запроса и отправляем запрос на получение подборки "):
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
            url=f"/compilations/{compilation_slug_podborka}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step("Проверяем, что в листинге подборки пустой массив субкатегорий"):
        assert response_public_compilation_1.json()["data"]["sub_menu"] == []

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение категории без субкатегорий "
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

        response_public_compilation_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug_category}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2.status_code == 200

    with allure.step("Проверяем, что в листинге по категории приходит только категория"):
        assert (
            response_public_compilation_2.json()["data"]["sub_menu"][0]["slug"]
            == compilation_slug_category
        )


@allure.id("1255")
@allure.title("Листинга по категории с субкатегориями")
@allure.description("Проверяем получение массива sub_menu в листинге по категории")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_sub_menu_in_category():
    compilation_gender = "female"
    compilation_slug = "platia"
    # compilation_slug_subcategory = "plate-kombinaciia"

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение категории с субкатегориями "
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

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step(
        "Проверяем, что в листинге категории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_1.json()["data"]["sub_menu"],
            ref_compilation_sub_menu,
        )

        assert result, "Не совпадает суб меню с эталоном"


@allure.id("1313")
@allure.title("Листинг по субкатегории с sub_menu")
@allure.description("Проверяем получение массива sub_menu в листинге по субкатегории")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_sub_menu_in_subcategory():
    compilation_gender = "female"
    compilation_slug = "plate-kombinaciia"

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение субкатегории с sub_menu "
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

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step(
        "Проверяем, что в листинге субкатегории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_1.json()["data"]["sub_menu"],
            ref_compilation_sub_menu,
        )

        assert result, "Не совпадает суб меню с эталоном"


@allure.id("1256")
@allure.title("Изменение сортировки sub_menu в листинге")
@allure.description(
    "Проверяем получение массива sub_menu в листинге по субкатегории с измененной сортировкой"
)
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_sub_menu_sorting_change():
    compilation_gender = "female"
    compilation_id = 66
    compilation_slug = "briuki-zenskie"
    compilation_slug_sub = "zen-briuki-cinos"

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение категории с sub_menu до изменения сортировки"
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

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step(
        "Проверяем, что в листинге субкатегории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_1.json()["data"]["sub_menu"],
            ref_compilation_sub_menu_before_sorting,
        )

    with allure.step("Изменяем сортировку субкатегорий"):
        compilation_sub_menu_data = json.dumps(
            {
                "public_title": "Брюки",
                "slug": "briuki-zenskie",
                "sub_categories": [
                    188,
                    201,
                    202,
                    200,
                    203,
                    189,
                    190,
                    191,
                    192,
                    193,
                    194,
                    195,
                ],
            }
        )

        response_private_put_compilation: Response = api.private_session.put(
            url=f"/compilations/{compilation_id}",
            data=compilation_sub_menu_data,
            headers={"Content-Type": "application/json"},
        )
        with allure.step(
            "Проверяем, что запрос на изменение сортировки субкатегори  прошел успешно"
        ):
            assert response_private_put_compilation.status_code == 200

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение категории с sub_menu после изменения сортировки"
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

        response_public_compilation_2_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2_1.status_code == 200

    with allure.step(
        "Проверяем, что в листинге субкатегории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_2_1.json()["data"]["sub_menu"],
            ref_compilation_sub_menu_after_sorting,
        )
    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение субкатегории с этой же родительской категорией с sub_menu после изменения сортировки"
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

        response_public_compilation_2_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug_sub}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2_2.status_code == 200

    with allure.step(
        "Проверяем, что в листинге субкатегории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_2_2.json()["data"]["sub_menu"],
            ref_compilation_sub_menu_after_sorting,
        )


@allure.id("1254")
@allure.title("Скрытая субкатегория не попадает в sub_menu в листинге")
@allure.description("Проверяем, что скрывая субкатегорию, она не попадает в массив sub_menu")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_get_listings_with_hidden_subcategory_in_sub_menu():
    compilation_gender = "female"
    # compilation_id = 15
    compilation_slug = "bizuteriia-zenskaia"
    compilation_slug_sub = "zen-braslety"
    compilation_id_hidden_subcategory = 361

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение категории с sub_menu до скрытия субкатегории"
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

        response_public_compilation_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_1.status_code == 200

    with allure.step(
        "Проверяем, что в листинге категории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_1.json()["data"]["sub_menu"],
            ref_compilation_sub_menu_before_hiding,
        )

    with allure.step("Удаляем/скрываем субкатегорию"):
        response_private_delete_compilation: Response = api.private_session.delete(
            url=f"/compilations/{compilation_id_hidden_subcategory}",
            headers={"Content-Type": "application/json"},
        )
        with allure.step("Проверяем, что запрос на удаление/скрытие субкатегории  прошел успешно"):
            assert response_private_delete_compilation.status_code == 200

    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение категории с sub_menu после удаления субкатегории"
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

        response_public_compilation_2_1: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2_1.status_code == 200

    with allure.step(
        "Проверяем, что в листинге категории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_2_1.json()["data"]["sub_menu"],
            ref_compilation_sub_menu_after_hiding,
        )
    with allure.step(
        "Формируем тело запроса и отправляем запрос на получение субкатегории с этой же родительской категорией с sub_menu после удаления субкатегории"
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

        response_public_compilation_2_2: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug_sub}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation_2_2.status_code == 200

    with allure.step(
        "Проверяем, что в листинге субкатегории приходит массив родительская категория + субкатегории"
    ):
        result = compare_sub_menu_with_reference(
            response_public_compilation_2_2.json()["data"]["sub_menu"],
            ref_compilation_sub_menu_after_hiding,
        )

    with allure.step("Восстанавливаем субкатегорию"):
        response_private_patch_compilation: Response = api.private_session.patch(
            url=f"/compilations/{compilation_id_hidden_subcategory}",
            headers={"Content-Type": "application/json"},
        )
        with allure.step("Проверяем, что запрос на восстановление субкатегории  прошел успешно"):
            assert response_private_patch_compilation.status_code == 200
