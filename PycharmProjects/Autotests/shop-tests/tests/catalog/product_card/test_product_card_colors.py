import allure
import json
from befree.api_model import api
from allure_commons.types import Severity
from befree.api_model.test_data.product_card.colors import product_articles
from requests import Response
import befree.api_model.product as pc


@allure.id("1280")
@allure.title("У товара все цвета активны")
@allure.description("Проверить, что в апи приходят только активные цвета")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_active_colors():
    kladr = "7800000000000"

    with allure.step("Отправляем запрос на получение товара, у которого все цвета активны"):
        product_api = pc.get_via_api(product_articles[0]["all_active_colors"]["article"], kladr)
    with allure.step("Проверяем, что все цвета пришли активными"):
        result = pc.compare_colors(
            product_api["colors"], product_articles[0]["all_active_colors"]["colors"]
        )
        assert result, "Некорректный состав массива colors[]"

    with allure.step("Отправляем запрос на получение товара, у которого цвета активны частично"):
        product_api = pc.get_via_api(product_articles[1]["part_active_colors"]["article"], kladr)
    with allure.step("Проверяем, что не все цвета пришли активными"):
        result = pc.compare_colors(
            product_api["colors"], product_articles[1]["part_active_colors"]["colors"]
        )
        assert result, "Некорректный состав массива colors[]"

    with allure.step("Отправляем запрос на получение товара, у которого нет активных цветов"):
        product_api = pc.get_via_api(product_articles[2]["none_active_colors"]["article"], kladr)
    with allure.step("Проверяем, что не все цвета пришли активными"):
        assert product_api["colors"] == [], "Не пустой состав массива colors[]"

    with allure.step("Отправляем запрос на получение товара, которого нет на стоке"):
        product_api = pc.get_via_api(product_articles[3]["empty_inventory"]["article"], kladr)
    with allure.step("Проверяем, что не все цвета пришли активными"):
        result = pc.compare_colors(
            product_api["colors"],
            product_articles[3]["empty_inventory"]["colors"],
        )
        assert result, "Некорректный состав массива colors[]"


@allure.id("1339")
@allure.title("Получение товара со сгруппированными цветами")
@allure.description("Проверить, что в апи приходят все цвета по отдельности")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_with_group_colors():
    kladr = "7800000000000"

    with allure.step(
        "Отправляем запрос на получение товара, у которого есть сгруппированные цвета"
    ):
        product_api = pc.get_via_api(product_articles[4]["with_group_of_colors"]["article"], kladr)
    with allure.step("Проверяем, что все цвета пришли по отдельности"):
        result = pc.compare_colors(
            product_api["colors"],
            product_articles[4]["with_group_of_colors"]["colors"],
        )
        assert result, "Некорректный состав массива colors[]"


@allure.id("1288")
@allure.title("Не приходит размер в colors[], если размер скрыт через вариант")
@allure.description(
    "Проверяем, что, если вариант скрыт, то по этому цвету не приходит размер при отправке запроса на получение товара"
)
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_without_size():
    kladr = "7800000000000"

    with allure.step("Отправляем запрос на получение товара, у которого скрытый вариант"):
        product_api = pc.get_via_api(product_articles[5]["without_size"]["article"], kladr)
    with allure.step(
        "Проверяем, что не приходит размер S, так как был скрыт вариант с этим размером"
    ):
        assert len(product_api["colors"][0]["sizes"]) == 3


@allure.id("1284")
@allure.title("Не приходит рост в colors[], если рост скрыт через вариант")
@allure.description(
    "Проверяем, что, если вариант скрыт, то по этому цвету не приходит рост при отправке запроса на получение товара"
)
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_without_height():
    kladr = "7800000000000"

    with allure.step("Отправляем запрос на получение товара, у которого скрытый вариант"):
        product_api = pc.get_via_api(product_articles[6]["without_height"]["article"], kladr)
    with allure.step(
        "Проверяем, что не приходит рост 164, так как был скрыт варианты с этими ростами"
    ):
        assert len(product_api["colors"][0]["heights"]) == 2


@allure.id("1284")
@allure.title("Сортировка цветов")
@allure.description("Проверяем, что сортировка цветов соответствует той, что установлена в админке")
@allure.tag("API Test")
@allure.feature("Сортировка")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_without_height():
    kladr = "7800000000000"

    with allure.step("Меняем сортировку цветов в товаре"):
        product_id = product_articles[7]["sorting_colors1"]["id"]

        colors_data = json.dumps([50, 37, 70, 1])
        response: Response = api.private_session.put(
            url=f"/products/{product_id}/colors_sort_order",
            data=colors_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200

    with allure.step("Отправляем запрос на получение товара после сортировки цветов"):
        product_api = pc.get_via_api(product_articles[7]["sorting_colors1"]["article"], kladr)

    with allure.step("Сравниваем сортировку с тем что в эталоне"):
        result = pc.compare_colors(
            product_api["colors"],
            product_articles[7]["sorting_colors1"]["colors"],
        )
        assert result, "Некорректный состав массива colors[]"

    with allure.step("Меняем сортировку цветов в товаре"):
        product_id = product_articles[7]["sorting_colors1"]["id"]

        colors_data = json.dumps([1, 37, 50, 70])
        response: Response = api.private_session.put(
            url=f"/products/{product_id}/colors_sort_order",
            data=colors_data,
            headers={"Content-Type": "application/json"},
        )
    with allure.step("Отправляем запрос на получение товара после еще одной сортировки цветов"):
        product_api = pc.get_via_api(product_articles[8]["sorting_colors2"]["article"], kladr)

    with allure.step("Сравниваем еще одну сортировку с тем что в эталоне"):
        result = pc.compare_colors(
            product_api["colors"],
            product_articles[8]["sorting_colors2"]["colors"],
        )
        assert result, "Некорректный состав массива colors[]"


@allure.id("1284")
@allure.title("Сортировка фото")
@allure.description(
    "Проверяем, что сортировка фото в товаре соответствует той, что установлена в админке"
)
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Сортировка")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_without_height():
    kladr = "7800000000000"

    with allure.step("Меняем сортировку фото в товаре"):
        product_id = product_articles[9]["sorting_photo1"]["id"]

        colors_data = json.dumps(
            [
                {"group": "1", "image_id": 167159, "sort_order": 0},
                {"group": "1", "image_id": 167160, "sort_order": 1},
                {"group": "1", "image_id": 167161, "sort_order": 2},
                {"group": "1", "image_id": 167162, "sort_order": 3},
                {"group": "1", "image_id": 167163, "sort_order": 4},
                {"group": "1", "image_id": 167164, "sort_order": 5},
                {"group": "1", "image_id": 167165, "sort_order": 6},
            ]
        )
        response: Response = api.private_session.put(
            url=f"/products/{product_id}/variations/233272/images",
            data=colors_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200

    with allure.step("Отправляем запрос на получение товара после сортировки фото"):
        product_api = pc.get_via_api(product_articles[9]["sorting_photo1"]["article"], kladr)

    with allure.step("Сравниваем сортировку с тем что в эталоне"):
        assert (
            product_api["colors"][0]["images"] == product_articles[9]["sorting_photo1"]["photo"]
        ), 'Некорректный состав массива colors["images"]'

    with allure.step("Меняем еще раз сортировку фото в товаре"):
        product_id = product_articles[10]["sorting_photo2"]["id"]

        colors_data = json.dumps(
            [
                {"group": "1", "image_id": 167159, "sort_order": 6},
                {"group": "1", "image_id": 167160, "sort_order": 5},
                {"group": "1", "image_id": 167161, "sort_order": 4},
                {"group": "1", "image_id": 167162, "sort_order": 3},
                {"group": "1", "image_id": 167163, "sort_order": 2},
                {"group": "1", "image_id": 167164, "sort_order": 1},
                {"group": "1", "image_id": 167165, "sort_order": 0},
            ]
        )
        response: Response = api.private_session.put(
            url=f"/products/{product_id}/variations/233272/images",
            data=colors_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200

    with allure.step("Отправляем запрос на получение товара после еще одной сортировки фото"):
        product_api = pc.get_via_api(product_articles[10]["sorting_photo2"]["article"], kladr)

    with allure.step("Сравниваем сортировку с тем что в эталоне"):
        assert (
            product_api["colors"][0]["images"] == product_articles[10]["sorting_photo2"]["photo"]
        ), 'Некорректный состав массива colors["images"]'
