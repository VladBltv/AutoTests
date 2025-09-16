import allure
import json
from befree.api_model import api, db_connection
from allure_commons.types import Severity
from requests import Response
import befree.api_model.stickers as st
from befree.api_model.catalog.public import CatalogPublic
from befree.api_model.test_data.product_card.stickers import stickers_list
import befree.api_model.product as pc


class TestProductCardGeneral(CatalogPublic):
    @allure.id("2581")
    @allure.title("Проверка вывода неизменяемых данных для товара")
    @allure.description("Проверить, что в апи корректно передаются неизменяемые данные для товара")
    @allure.tag("API Test")
    @allure.severity(Severity.MINOR)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    def test_immutable_data_for_product_card(self):
        kladr = "7800000000000"
        with allure.step("Выбираем из бд первый попавшийся товар"):
            product_database = pc.random_from_database()

        with allure.step("Отправляем апи запрос на получение товара"):
            product_api = pc.get_via_api(product_database[0]["article"], kladr)

        with allure.step("Сравнение неизменяемых данных для товара"):
            assert (
                product_database[0]["id"] == product_api["id"]
                and product_database[0]["article"] == product_api["article"]
                and product_database[0]["title"] == product_api["title"]
                and product_database[0]["marketing_title"] == product_api["marketing_title"]
                and product_database[0]["category_id"] == product_api["category"]["id"]
                and product_database[0]["public_title"] == product_api["category"]["name"]
                and product_database[0]["slug"] == product_api["category"]["slug"]
                and product_database[0]["gender"] == product_api["gender"]
            )

    @allure.id("2582")
    @allure.title("Проверка вывода изменяемых  безусловных данных для товара")
    @allure.description(
        "Проверить, что в апи корректно передаются изменяемые и безусловные данные для товара"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.MINOR)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    def test_changeable_data_for_product_card(self):
        kladr = "7800000000000"
        with allure.step("Выбираем из бд первый попавшийся товар"):
            product_database = pc.random_from_database()

        with allure.step("Изменяем данные в категории"):
            category_data = json.dumps(
                {
                    "public_title": product_database[0]["public_title"],
                    "slug": product_database[0]["slug"],
                    "is_category": 1,
                    "filter_type": "filter",
                    "size_table_image_product": 1,
                    "size_table_image_figure": 29,
                    "seo_description": "Befree",
                }
            )

            response_private_put_category: Response = api.private_session.put(
                url=f"/compilations/{product_database[0]['category_id']}",
                data=category_data,
                headers={"Content-Type": "application/json"},
            )

        with allure.step("Проверяем, что запрос прошел успешно"):
            assert response_private_put_category.status_code == 200

        with allure.step("Отправляем апи запрос на получение товара"):
            product_api = pc.get_via_api(product_database[0]["article"], kladr)

        with allure.step("Сравниваем изменяемые безусловные поля"):
            assert (
                product_api["category"]["seo"]["description"] == "Befree"
                and product_api["category"]["size_table_image_product"] == 1
                and product_api["category"]["size_table_image_figure"] == 29
            )

    @allure.id("2583")
    @allure.title("Проверка вывода города для товара")
    @allure.description("Проверить, что в апи корректно передается город для товара")
    @allure.tag("API Test")
    @allure.severity(Severity.NORMAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    def test_product_card_city(self):
        with allure.step("Выбираем из бд первый попавшийся товар"):
            product_database = pc.random_from_database()

        with allure.step("Устанавливаем КЛАДР гСПБ"):
            kladr = "7800000000000"

        with allure.step("Отправляем апи запрос на получение товара"):
            product_api_spb = pc.get_via_api(product_database[0]["article"], kladr)

        with allure.step("Получаем из БД данные по гСПБ"):
            city_data_query = f"""
                            select c.id, c.title, c.dadata_kladr, c.omni_2  
                            from cities c
                            join stores s on s.city_id = c.id
                            where c.dadata_kladr = '{kladr}'
                            GROUP BY c.id
                            HAVING COUNT(s.id) > 1000
            """
            city_data_database = db_connection.catalog.get_data(city_data_query)

        with allure.step("Сравниваем данные по городу через апи и БД"):
            if city_data_database != []:
                assert (
                    product_api_spb["city"]["id"] == city_data_database[0]["id"]
                    and product_api_spb["city"]["name"] == city_data_database[0]["title"]
                    and product_api_spb["city"]["kladr"] == city_data_database[0]["dadata_kladr"]
                    and product_api_spb["city"]["omni_2"] == city_data_database[0]["omni_2"]
                    and product_api_spb["city"]["is_has_stores"] == 1
                )

        with allure.step("Устанавливаем КЛАДР Собакино"):
            kladr = "5004800024300"

        with allure.step("Отправляем апи запрос на получение товара"):
            product_api_sobakino = pc.get_via_api(product_database[0]["article"], kladr)

        with allure.step("Получаем из БД данные по Собакино"):
            city_data_query = f"""
                               select c.id, c.title, c.dadata_kladr, c.omni_2  
                               from cities c
                               join stores s on s.city_id = c.id
                               where c.dadata_kladr = '{kladr}'
                               GROUP BY c.id
                               HAVING COUNT(s.id) > 1000
               """
            city_data_database = db_connection.catalog.get_data(city_data_query)

        with allure.step("Сравниваем данные по городу через апи и БД"):
            if city_data_database == []:
                assert (
                    product_api_sobakino["city"]["id"] == None
                    and product_api_sobakino["city"]["name"] == None
                    and product_api_sobakino["city"]["kladr"] == kladr
                    and product_api_sobakino["city"]["omni_2"] == 0
                    and product_api_sobakino["city"]["is_has_stores"] == 0
                )

    @allure.id("2584")
    @allure.title("Проверка страницы товара со стикерами")
    @allure.description("Проверить, что в апи корректно передаются стикеры для товара")
    @allure.tag("API Test")
    @allure.feature("Стикеры")
    @allure.severity(Severity.NORMAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    def test_product_card_stickers(self):
        kladr = "7800000000000"
        with allure.step("Выбираем из бд первый попавшийся товар без стикера"):
            product_database = pc.random_from_database_without_stickers()

        with allure.step("Отправляем апи запрос на получение товара"):
            product_api = pc.get_via_api(product_database[0]["article"], kladr)

        with allure.step("Проверяем, что товар приходит без стикера"):
            assert product_api["stickers"] == []

        with allure.step("Добавление к товару кастомного стикера CO:CREATE"):
            st.edit_with_list_of_articles(stickers_list[2], product_database[0]["article"], "add")

        with allure.step("Проверяем, вывод кастомного стикера"):
            product_api = pc.get_via_api(product_database[0]["article"], kladr)

            assert (
                product_api["stickers"][0]["id"] == stickers_list[2]["id"]
                and product_api["stickers"][0]["text"] == stickers_list[2]["title"]
            )

        with allure.step("Добавляем стикер hit"):
            st.edit_with_list_of_articles(stickers_list[1], product_database[0]["article"], "add")

        with allure.step("Проверяем вывод стикеров hit + кастомный"):
            pc.check_stickers(
                product_database[0]["article"],
                kladr,
                [stickers_list[1], stickers_list[2]],
            )

        with allure.step("Добавляем стикер new"):
            st.edit_with_list_of_articles(stickers_list[0], product_database[0]["article"], "add")

        with allure.step("Проверяем вывод стикеров hit + кастомный (без new)"):
            pc.check_stickers(
                product_database[0]["article"],
                kladr,
                [stickers_list[1], stickers_list[2]],
            )

        with allure.step("Удаляем стикер hit"):
            st.edit_with_list_of_articles(
                stickers_list[1], product_database[0]["article"], "delete"
            )

        with allure.step("Проверяем вывод стикеров new + кастомный"):
            pc.check_stickers(
                product_database[0]["article"],
                kladr,
                [stickers_list[0], stickers_list[2]],
            )
        with allure.step("Удаляем кастомный стикер"):
            st.edit_with_list_of_articles(
                stickers_list[2], product_database[0]["article"], "delete"
            )
        with allure.step("Проверяем вывод стикера new"):
            pc.check_stickers(
                product_database[0]["article"],
                kladr,
                [stickers_list[0]],
            )
        with allure.step("Добавляем стикер hit"):
            st.edit_with_list_of_articles(stickers_list[1], product_database[0]["article"], "add")
        with allure.step("Проверяем вывод стикеров hit + new"):
            pc.check_stickers(
                product_database[0]["article"],
                kladr,
                [stickers_list[1], stickers_list[0]],
            )
        with allure.step("Удаляем стикер new"):
            st.edit_with_list_of_articles(
                stickers_list[0], product_database[0]["article"], "delete"
            )
        with allure.step("Проверяем вывод стикера hit"):
            pc.check_stickers(
                product_database[0]["article"],
                kladr,
                [stickers_list[1]],
            )

    @allure.id("2383")
    @allure.title("Регистронезависимость метода получения товара")
    @allure.description(
        "Проверить, что  метод получения товара работает независимо от регистра букв " "артикула"
    )
    @allure.tag("API Test")
    @allure.feature("Стикеры")
    @allure.severity(Severity.NORMAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    def test_case_insensitive_article(self):
        with allure.step("Берем артикул, у которого в бд все буквы верхнего регистра"):
            article = "BWT"

        with allure.step(
            "Отправляем запрос на получение товара по этому артикулу с буквами в нижнем регистре"
        ):
            article_with_change = "bwt"

            product_response = self.api_product.get(article=article_with_change)
            assert product_response.status_code == 200

        with allure.step("Проверяем, что в ответе приходит артикул в верхнем регистре"):
            assert product_response.json()["data"]["article"] == article

        with allure.step("Берем артикул, у которого в бд все буквы нижнего регистра"):
            article = "bamboo_bra1"

        with allure.step(
            "Отправляем запрос на получение товара по этому артикулу с буквами в верхнем регистре"
        ):
            article_with_change = "BAMBOO_BRA1"

            product_response = self.api_product.get(article=article_with_change)
            assert product_response.status_code == 200

        with allure.step("Проверяем, что в ответе приходит артикул в нижнем регистре"):
            assert product_response.json()["data"]["article"] == article

        with allure.step(
            "Берем артикул, у которого в бд есть буквы и нижнего, и верхнего регистра, и цифры"
        ):
            article = "BananasSSNEWcol62"

        with allure.step(
            "Отправляем запрос на получение товара по этому артикулу с измененениями регистра букв"
        ):
            article_with_change = "banANAsSsNeWcoL62"

            product_response = self.api_product.get(article=article_with_change)
            assert product_response.status_code == 200

        with allure.step("Проверяем, что в ответе приходит артикул как в бд"):
            assert product_response.json()["data"]["article"] == article
