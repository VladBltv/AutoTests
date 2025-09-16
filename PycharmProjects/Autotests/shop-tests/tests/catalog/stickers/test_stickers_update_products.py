import allure
from allure_commons.types import Severity
from requests import Response

from befree.api_model import api, db_connection
from befree.api_model.stickers import (
    get_sticker_by_id_via_api,
    get_10_products_without_custom_sticker,
    empty_sticker_given,
    sticker_with_products_given,
    get_products_by_sticker_id,
    get_any_products_with_custom_sticker,
    any_custom_sticker_given,
)
from utils import array
from utils.data_generation import rand_str
from utils import files


@allure.id("1192")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title(
    "Добавление к стикеру товаров, которые не привязаны ни к какому стикеру, через список"
)
@allure.description(
    "Проверяем добавление к стикеру товаров, которые не привязаны ни к какому стикеру, через загрузку списка"
)
def test_stickers_add_products_free_as_list():
    with allure.step("Находим товары, которые не привязаны ни к какому стикеру"):
        products = get_10_products_without_custom_sticker()
        articles = [i["article"] for i in products]

    with allure.step("Находим стикер без товаров"):
        sticker = empty_sticker_given()

    with allure.step("Формируем данные для стикера"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "add",
            "products_articles": ",".join(articles),
        }

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step(
        "Проверяем, что счетчик товаров в стикере соответствует переданному количеству товаров"
    ):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == len(articles)

    with allure.step("Проверяем, что к переданным товарам привязан нужный стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value


@allure.id("1205")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title(
    "Добавление к стикеру товаров, которые уже привязаны к какому то стикеру, через список"
)
@allure.description(
    "Проверяем добавление к стикеру товаров, которые уже привязаны к другому стикеру, через загрузку списка"
)
def test_stickers_add_products_occupied_as_list():
    with allure.step("Находим товары, которые привязаны к какому-либо стикеру"):
        products = get_any_products_with_custom_sticker()
        articles = products[0]["articles"].split(",")
        sticker_id_old = products[0]["sticker_custom"]

    with allure.step("Находим пустой стикер, к которому будем перепривязывать товары"):
        sticker = empty_sticker_given()

    with allure.step("Формируем данные для привязки к новому стикеру"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "add",
            "products_articles": ",".join(articles),
        }

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step(
        "Проверяем, что счетчик товаров в стикере соответствует переданному количеству товаров"
    ):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == len(articles)

    with allure.step("Проверяем, что к переданным товарам привязан нужный стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value
        assert sticker_value != sticker_id_old

    with allure.step("Проверяем, что к старому стикеру больше не привязаны товары"):
        response_get = get_sticker_by_id_via_api(sticker_id_old)
        assert response_get["data"]["products_count"] == 0


@allure.id("1201")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Добавление к стикеру товаров, которые не привязаны ни к какому стикеру, через файл")
@allure.description(
    "Проверяем добавление к стикеру товаров, которые не привязаны ни к какому стикеру, через загрузку файла"
)
def test_stickers_add_products_free_as_file():
    with allure.step("Находим товары, которые не привязаны ни к какому стикеру"):
        products = get_10_products_without_custom_sticker()
        articles = [i["article"] for i in products]

    with allure.step("Находим стикер без товаров"):
        sticker = empty_sticker_given()

    with allure.step("Запишем артикулы в файл"):
        files.write_lines(files.generate_absolute_path("resources/articles.csv"), articles)

    with allure.step("Формируем данные для стикера"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "add",
        }

        test_file = open(files.generate_absolute_path("resources/articles.csv"), "rb")

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}",
            data=request_data,
            files={"products_file": test_file},
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step(
        "Проверяем, что счетчик товаров в стикере соответствует переданному количеству товаров"
    ):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == len(articles)

    with allure.step("Проверяем, что к переданным товарам привязан нужный стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value


@allure.id("1194")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title(
    "Добавление к стикеру товаров, которые уже привязаны  к какому то стикеру, через файл"
)
@allure.description(
    "Проверяем добавление к стикеру товаров, которые уже привязаны к какому-то стикеру, через загрузку файла"
)
def test_stickers_add_products_occupied_as_file():
    with allure.step("Находим товары, которые привязаны к какому-либо стикеру"):
        products = get_any_products_with_custom_sticker()
        articles = products[0]["articles"].split(",")
        sticker_id_old = products[0]["sticker_custom"]

    with allure.step("Находим пустой стикер, к которому будем перепривязывать товары"):
        sticker = empty_sticker_given()

    with allure.step("Запишем артикулы в файл"):
        files.write_lines(files.generate_absolute_path("resources/articles.csv"), articles)

    with allure.step("Формируем данные для привязки к новому стикеру"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "add",
        }

        test_file = open(files.generate_absolute_path("resources/articles.csv"), "rb")

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}",
            data=request_data,
            files={"products_file": test_file},
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step(
        "Проверяем, что счетчик товаров в стикере соответствует переданному количеству товаров"
    ):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == len(articles)

    with allure.step("Проверяем, что к переданным товарам привязан нужный стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value
        assert sticker_value != sticker_id_old

    with allure.step("Проверяем, что к старому стикеру больше не привязаны товары"):
        response_get = get_sticker_by_id_via_api(sticker_id_old)
        assert response_get["data"]["products_count"] == 0


@allure.id("1178")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Добавление товаров к стикеру, в котором уже есть товары, через список")
@allure.description(
    "Проверяем добавление к товаров к стикеру, в котором уже есть товары, через загрузку списка"
)
def test_stickers_add_products_partial_presence_as_file():
    with allure.step("Находим стикер, в котором привязаны продукты"):
        sticker = sticker_with_products_given()

    with allure.step("Находим товары, к которым привязан стикер"):
        products = get_products_by_sticker_id(sticker["id"])
        articles = [i["article"] for i in products]

    with allure.step("Находим товары, которые не привязаны ни к какому стикеру"):
        products_free = get_10_products_without_custom_sticker()
        articles_free = [i["article"] for i in products_free]

    with allure.step("Объединим уже привязанные артикулы и новые артикулы"):
        articles_union = articles + articles_free

    with allure.step("Запишем артикулы в файл"):
        files.write_lines(files.generate_absolute_path("resources/articles.csv"), articles_union)

    with allure.step("Формируем данные для привязки к стикеру"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "add",
        }

        test_file = open(files.generate_absolute_path("resources/articles.csv"), "rb")

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}",
            data=request_data,
            files={"products_file": test_file},
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step(
        "Проверяем, что счетчик товаров в стикере соответствует переданному количеству товаров"
    ):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == len(articles_union)

    with allure.step("Проверяем, что к переданным товарам привязан нужный стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value


@allure.id("1182")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Полная очистку списка товаров у стикера")
@allure.description("Проверяем полную очистку списка товаров у стикера")
def test_stickers_clear():
    with allure.step("Находим стикер, в котором привязаны продукты"):
        sticker = sticker_with_products_given()

    with allure.step("Находим товары, к которым привязан стикер"):
        products = get_products_by_sticker_id(sticker["id"])
        articles = [i["article"] for i in products]

    with allure.step("Формируем данные для отправки в запрос"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "PUT",
        }

    with allure.step("Отправляем запрос на очистку"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step("Проверяем, что счетчик товаров у стикера 0"):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == 0

    with allure.step("Проверяем, что к переданным товарам больше не привязан стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker_value is None


@allure.id("1193")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Полная очистку списка товаров у стикера через опцию удаления")
@allure.description("Проверяем полную очистку списка товаров у стикера через опцию удаления")
def test_stickers_delete_all():
    with allure.step("Находим стикер, в котором привязаны продукты"):
        sticker = sticker_with_products_given()

    with allure.step("Находим товары, к которым привязан стикер"):
        products = get_products_by_sticker_id(sticker["id"])
        articles = [i["article"] for i in products]

    with allure.step("Формируем данные для для отправки в запрос"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "delete",
            "products_articles": ",".join(articles),
        }

    with allure.step("Отправляем запрос на очистку"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step("Проверяем, что счетчик товаров у стикера 0"):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == 0

    with allure.step("Проверяем, что к переданным товарам больше не привязан стикер"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker_value is None


@allure.id("1181")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Частичная очистка списка товаров у стикера через опцию удаления")
@allure.description("Проверяем частичное удаление товаров у стикера через опцию удаления")
def test_stickers_delete_part():
    with allure.step("Находим стикер, в котором привязаны продукты"):
        sticker = sticker_with_products_given()

    with allure.step("Находим товары, к которым привязан стикер"):
        products = get_products_by_sticker_id(sticker["id"])
        articles = [i["article"] for i in products]

    with allure.step(
        "Разделим массив товаров на два: артикулы, которые удалим и артикулы, которые оставим"
    ):
        articles_for_delete = array.split(articles)[0]
        articles_for_remain = array.split(articles)[1]

    with allure.step("Формируем данные для отправки в запрос"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "delete",
            "products_articles": ",".join(articles_for_delete),
        }

    with allure.step("Отправляем запрос на удаление части артикулов"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step("Проверяем, что счетчик в стикере уменьшился на количество удаленных товаров"):
        response_get = get_sticker_by_id_via_api(sticker["id"])
        assert response_get["data"]["products_count"] == len(articles) - len(articles_for_delete)

    with allure.step("Проверяем, что у удаленных товаров стикер больше не привязан"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles_for_delete)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker_value is None

    with allure.step("Проверяем, что у оставшихся продуктов стикер остался привязанным"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles_for_remain)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value


@allure.id("1179")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Одновременно очистка и загрузка новых товаров в стикер")
@allure.description("Проверяем одновременную очистку и загрузку новых товаров в стикер")
def test_stickers_clear_and_add():
    with allure.step("Находим стикер, в котором привязаны продукты"):
        sticker = sticker_with_products_given()

    with allure.step("Находим товары, к которым привязан стикер"):
        products_with_sticker = get_products_by_sticker_id(sticker["id"])
        articles_with_sticker = [i["article"] for i in products_with_sticker]

    with allure.step("Находим товары, которые не привязаны ни к какому стикеру"):
        products_clear = get_10_products_without_custom_sticker()
        articles_clear = [i["article"] for i in products_clear]

    with allure.step("Формируем данные для изменения стикера"):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "clear",
            "products_articles": ",".join(articles_clear),
        }

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step("Проверяем, что старые товары отвызались от стикера"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles_with_sticker)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker_value is None

    with allure.step("Проверяем, что новые товары привязались к стикеру"):
        query = f"""
            select p.sticker_custom 
            from products p  
            where p.article in {tuple(articles_clear)}
            group by p.sticker_custom
        """
        sticker_value = db_connection.catalog.get_data(query)[0]["sticker_custom"]
        assert sticker["id"] == sticker_value


@allure.id("1190")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.suite("Product")
@allure.feature("Стикеры")
@allure.label("owner", "Potegova")
@allure.label("service", "Catalog")
@allure.title("Загрузку артикула, которого нет в базе")
@allure.description(
    "Проверяем загрузку артикула, которого нет в базе, артикул должен проигнорироваться"
)
def test_send_wrong_article():
    with allure.step("Находим любой кастомный стикер"):
        sticker = any_custom_sticker_given()

    with allure.step(
        "Формируем данные для изменения стикера с использованием несуществующего артикула"
    ):
        request_data = {
            "title": sticker["title"],
            "front_color_hex": sticker["front_color_hex"],
            "front_bg_color_hex": sticker["front_bg_color_hex"],
            "is_visible": "1",
            "_method": "PUT",
            "product_action_flag": "add",
            "products_articles": rand_str(n=8),
        }

    with allure.step("Отправляем данные в стикер"):
        response_post: Response = api.private_session.post(
            url=f"/stickers/{sticker['id']}", data=request_data
        )

    with allure.step("Получаем данные по стикеру после обновления"):
        sticker_updated = get_sticker_by_id_via_api(sticker["id"])

    with allure.step("Проверяем, что ответ успешный"):
        assert response_post.status_code == 200

    with allure.step("Проверяем, что счетчик по стикеру не изменился"):
        sticker["products_count"] == sticker_updated["data"]["products_count"]
