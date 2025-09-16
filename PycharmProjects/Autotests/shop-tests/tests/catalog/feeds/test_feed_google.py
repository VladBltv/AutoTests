import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files, helpers
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from pytest_check import check
import random
import os


class TestFeedGoogle(QueriesCatalog):
    @allure.id("2557")
    @allure.title("Фид google: оферы")
    @allure.label("service", "Catalog")
    @allure.feature("Google", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """
        Требования к формированию фида

        Для наполнения items должны выполняться следующие условия
        Товар не в заморозке по складу fulfilment
        Товар не помечен на удаление
        Остаток товара по складу fulfilment > 2
        Консольная команда для генерации фида: php artisan befree:generate_feed google
        Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/google.xml
    """
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_google_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed google"""
                pass
        with allure.step("Запросить фид"):
            feed_google: Response = api.storage_session.get("/storage/feeds/google.xml")
            assert feed_google.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/google.xml"), feed_google.text)
            files.xml_to_json(files.generate_absolute_path("resources/google.xml"), "google")

            google_feed_data = json.loads(files.read(files.generate_absolute_path("resources/google.json")))

        with allure.step("Сформировать в базе список вариантов подпадающих под условия отбора в фида"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            query = f"""
                        select v.id
                        from variations as v 
                        join products as p on v.product_id=p.id 
                        where v.fulfilment_qty >= {min_qty_ff} and v.deleted_at is null and p.fulfilment_frozen is false
                    """

            offers_base = list(map(lambda n: n["id"], db_connection.catalog.get_data(query)))

            with allure.step("Варианты из списка совпадают с вариантами в фиде"):
                offers_feed = list(
                    map(
                        lambda n: int(n["g:id"]),
                        google_feed_data["rss"]["channel"]["item"],
                    )
                )

                assert len(list(set(offers_base) ^ set(offers_feed))) == 0

    @allure.id("2558")
    @allure.title("Фид google структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Google", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe google")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_google_data_structure(self):
        with allure.step("Запросить фид"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            feed_google: Response = api.storage_session.get("/storage/feeds/google.xml")
            check.equal(feed_google.status_code, 200, "Feed request should return 200 status code")

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/google.xml"), feed_google.text)
            files.xml_to_json(files.generate_absolute_path("resources/google.xml"), "google")

            google_feed_data = json.loads(files.read(files.generate_absolute_path("resources/google.json")))

            offers = google_feed_data["rss"]["channel"]["item"]

        with allure.step("Проверить, что поле g:item_group_id соответствует id продукта"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти id варианта офера"):
                variation_id = random_offer["g:id"]

            with allure.step("Найти продукт в базе по id варианта"):
                product_data = self.get_product_by_variation(variation_id)

            with allure.step("Проверить, что поле g:item_group_id соответствует id продукта"):
                check.equal(
                    random_offer["g:item_group_id"],
                    str(product_data["id"]),
                )
        with allure.step("Проверить формирование поля g:brand"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что поле g:brand имеет значение befree"):
                check.equal(
                    random_offer["g:brand"],
                    "befree",
                )

        with allure.step("Проверить формирование поля g:title"):
            with allure.step("Найти в базе продукт без маркетингового названия"):
                conditions = ["and p.marketing_title is null"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)
                product_id = variation_data["product_id"]
                product_data = self.entity_by_id(table="products", id=product_id)

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(
                    filter(
                        lambda item: item["g:item_group_id"] == str(product_id),
                        google_feed_data["rss"]["channel"]["item"],
                    )
                )

            with allure.step("Проверить, что поле g:title соответствует наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["g:title"]),
                    product_data["title"],
                )

            with allure.step("Найти в базе продукт c маркетинговым наименованием"):
                conditions = ["and p.marketing_title is not null"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)
                product_id = variation_data["product_id"]
                product_data = self.entity_by_id(table="products", id=product_id)

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(
                    filter(
                        lambda item: item["g:item_group_id"] == str(product_id),
                        google_feed_data["rss"]["channel"]["item"],
                    )
                )

            with allure.step("Проверить, что поле g:title соответствует маркетинговому наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["g:title"]),
                    product_data["marketing_title"],
                )

        with allure.step("Проверить формирование поля g:google_product_category"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Взять id варианта офера"):
                variation_id = random_offer["g:id"]

            with allure.step("Получить данные о товаре в базе по id товара"):
                product_data = self.entity_by_id(table="products", id=random_offer["g:item_group_id"])

            with allure.step("Получить данные о категории товара в базе по id продукта"):
                category_data = self.entity_by_id(table="compilations", id=product_data["category_id"])

            with allure.step(
                "Проверить, что поле g:google_product_category соответствует значению поля google_product_category_id"
            ):
                check.equal(
                    random_offer["g:google_product_category"],
                    str(category_data["google_product_category_id"]),
                )

        with allure.step("Проверить формирование поля g:gtin и g:mpn"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти id варианта офера"):
                variation_id = random_offer["g:id"]

            with allure.step("Найти вариант в базе по id варианта"):
                variation_data = self.entity_by_id(table="variations", id=variation_id)

            with allure.step("Проверить, что поле g:gtin соответствует sku варианта"):
                check.equal(
                    random_offer["g:gtin"],
                    variation_data["sku"],
                )

            with allure.step("Проверить, что поле g:mpn соответствует sku варианта"):
                check.equal(
                    random_offer["g:mpn"],
                    variation_data["sku"],
                )

        with allure.step("Проверить формирование поля g:condition"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что значение поля g:condition равно new"):
                check.equal(
                    random_offer["g:condition"],
                    "new",
                )

        with allure.step("Проверить формирование поля g:price и g:sale_price"):
            with allure.step("Найти в базе товар, у которого current_price == maximum_price"):
                conditions = ["and v.current_price = v.maximum_price"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )

                variation_id = offers_base[0]["variation_id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)

                feed_offer = list(filter(lambda item: item["g:id"] == str(variation_id), offers))

            with allure.step("Проверить, что поле g:price соответствует current_price варианта"):
                check.equal(
                    feed_offer[0]["g:price"],
                    str(variation_data["current_price"]) + " RUB",
                )

            with allure.step("Проверить, что поле g:sale_price соответствует current_price варианта"):
                check.equal(
                    feed_offer[0]["g:sale_price"],
                    str(variation_data["current_price"]) + " RUB",
                )

            with allure.step(
                "Найти в базе товар, у которого current_price != maximum_price и параметр crossout = False"
            ):
                conditions = ["and v.current_price != v.maximum_price and v.crossout = False"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )

                variation_id = offers_base[0]["variation_id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)

                feed_offer = list(filter(lambda item: item["g:id"] == str(variation_id), offers))

            with allure.step("Проверить, что поле g:price соответствует current_price варианта"):
                check.equal(
                    feed_offer[0]["g:price"],
                    str(variation_data["current_price"]) + " RUB",
                )

            with allure.step("Проверить, что поле g:sale_price соответствует current_price варианта"):
                check.equal(
                    feed_offer[0]["g:sale_price"],
                    str(variation_data["current_price"]) + " RUB",
                )

            with allure.step(
                "Найти в базе товар, у которого current_price != maximum_price и параметр crossout = True"
            ):
                conditions = ["and v.current_price != v.maximum_price and v.crossout = True"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )

                variation_id = offers_base[0]["variation_id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)

                feed_offer = list(filter(lambda item: item["g:id"] == str(variation_id), offers))

            with allure.step("Проверить, что поле g:price соответствует maximum_price варианта"):
                check.equal(
                    feed_offer[0]["g:price"],
                    str(variation_data["maximum_price"]) + " RUB",
                )

            with allure.step("Проверить, что поле g:sale_price соответствует current_price варианта"):
                check.equal(
                    feed_offer[0]["g:sale_price"],
                    str(variation_data["current_price"]) + " RUB",
                )

        with allure.step("Проверить формирование поля g:availability"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что значение поля g:availability равно in_stock"):
                check.equal(
                    random_offer["g:availability"],
                    "in_stock",
                )

        with allure.step("Проверить формирование поля g:size"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

                variation_id = random_offer["g:id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)
                size_data = self.entity_by_id(table="sizes", id=variation_data["size_id"])

            with allure.step("Проверить, что значение поля g:size соответствует размеру варианта"):
                check.equal(
                    helpers.decode_unicode(random_offer["g:size"]),
                    size_data["value"],
                )

        with allure.step("Проверить формирование поля g:color"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

                variation_id = random_offer["g:id"]
                variation_data = self.entity_by_id(table="variations", id=variation_id)
                color_data = self.entity_by_id(table="colors", id=variation_data["color_id"])

            with allure.step("Проверить, что значение поля g:color соответствует цвету варианта"):
                check.equal(
                    helpers.decode_unicode(random_offer["g:color"]),
                    color_data["value"],
                )

        with allure.step("Проверить наличие в фиде полей g:description, g:image_link"):
            with allure.step("Найти рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле description"):
                check.equal("g:description" in random_offer, True, "Description should be present")

            with allure.step("Проверить, что в офере есть поле image_link"):
                check.equal("g:image_link" in random_offer, True, "Image_link should be present")

        with allure.step("Проверить формирование поля g:link"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в оффере есть поле g:link"):
                check.equal("g:link" in random_offer, True, "g:link should be present")

            with allure.step("Найти в базе вариант продукта по id из рандомного офера"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["g:id"])

            with allure.step("Найти в базе продукт по id товара"):
                product_data = self.entity_by_id(table="products", id=random_offer["g:item_group_id"])

            with allure.step("Проверить, что в оффере g:link соответствует url продукта"):
                gender = "zhenskaya" if product_data["gender"] == "female" else "muzhskaya"
                url = (
                    f"{os.getenv('SHOP_URL')}/{gender}/product/{product_data['article']}/{variation_data['color_code_id']}?size={variation_data['size_id']}&height={variation_data['height_id']}"
                    if variation_data["height_id"]
                    else f"{os.getenv('SHOP_URL')}/{gender}/product/{product_data['article']}/{variation_data['color_code_id']}?size={variation_data['size_id']}&height="
                )
                check.equal(random_offer["g:link"], url, "Url mismatch")
