import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from utils import helpers
from pytest_check import check
import random
import os


class TestFeedFlocktory(QueriesCatalog):
    @allure.id("2555")
    @allure.title("Фид flocktory: категории и оферы")
    @allure.label("service", "Catalog")
    @allure.feature("Flocktory", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """
            Требования к формированию фида

            Формат файла xml
            Включаем в фид только варианты, подходящие под ВСЕ условия:
            
            Остатки на складах фулфилмента > 1
            В таблице product_inventories имеются остатки по магазину, имеющему type =fulfilment
            Вариант не удален
            Свойство варианта deleted_at is null
            Вариант не в заморозке для складов фулфилмента
            Свойство продукта, которому принадлежит вариант fulfilment_frozen =false
            Текущая цена не равна 0
            Свойство варианта current_price != 0
            Консольная команда для генерации фида: php artisan befree:generate_feed flocktory
            Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/flocktory.xml
            
            Дока https://confluence.melonfashion.ru/pages/viewpage.action?pageId=1121653278
        """
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_flocktory_categories_and_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed flocktory"""
                pass
        with allure.step("Запросить фид"):
            feed_flocktory: Response = api.storage_session.get("/storage/feeds/flocktory.xml")
            assert feed_flocktory.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/flocktory.xml"), feed_flocktory.text)
            files.xml_to_json(files.generate_absolute_path("resources/flocktory.xml"), "flocktory")

            flocktory_feed_data = json.loads(files.read(files.generate_absolute_path("resources/flocktory.json")))

        with allure.step("Сформировать в базе список актуальных id категорий, включая подборки"):
            categories_base = list(map(lambda n: n["id"], self.get_active_compilations()))

            with allure.step("Список должен совпадать со списком категорий в фиде"):
                categories_feed = list(
                    map(
                        lambda n: int(n["@id"]),
                        flocktory_feed_data["yml_catalog"]["shop"]["categories"]["category"],
                    )
                )

                assert len(list(set(categories_base) ^ set(categories_feed))) == 0
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
                        lambda n: int(n["@id"]),
                        flocktory_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                    )
                )

            assert len(list(set(offers_base) ^ set(offers_feed))) == 0

    @allure.id("2556")
    @allure.title("Фид flocktory структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Flocktory", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe flocktory")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_flocktory_data_structure(self):
        with allure.step("Запросить фид"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            feed_flocktory: Response = api.storage_session.get("/storage/feeds/flocktory.xml")
            assert feed_flocktory.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/flocktory.xml"), feed_flocktory.text)
            files.xml_to_json(files.generate_absolute_path("resources/flocktory.xml"), "flocktory")

            flocktory_feed_data = json.loads(files.read(files.generate_absolute_path("resources/flocktory.json")))

            offers = flocktory_feed_data["yml_catalog"]["shop"]["offers"]["offer"]

        with allure.step("Проверить, что в поле @group_id соответстует id продукта"):
            with allure.step("Найти в базе товар в наличии на складе fulfilment"):
                offers_base = self.find_variation_by_availability_condition(qty_ff=f">= {min_qty_ff}")
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Найти в базе продукт по id варианта"):
                product_data = self.get_product_by_variation(variation_id)

            with allure.step("Проверить, что в поле @group_id соответстует id продукта"):
                check.equal(feed_offer[0]["@group_id"], str(product_data["id"]), "Group id mismatch")

        with allure.step("Проверить формирования полей price и oldprice"):
            with allure.step("Найти в базе товар, у которого current_price == maximum_price"):
                conditions = ["and v.current_price = v.maximum_price"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Проверить, что в оффере нет поля oldprice"):
                check.equal("oldprice" not in feed_offer[0], True, "Oldprice should not be present")

            with allure.step("Проверить, что в оффере есть поле price и в него передается значение current_price"):
                current_price = self.entity_by_id(table="variations", id=variation_id)["current_price"]
                check.equal(feed_offer[0]["price"], str(current_price), "Price mismatch")

            with allure.step("Проверить, что в оффере нет параметра  Скидка"):
                discount_param = list(
                    filter(
                        lambda param: param["@name"] == helpers.code_unicode("Скидка"),
                        feed_offer[0]["param"],
                    )
                )
                check.equal(len(discount_param), 0, "Discount param should not be present")

            with allure.step(
                "Найти в базе товар, у которого current_price != maximum_price и параметр crossout = False"
            ):
                conditions = ["and v.current_price != v.maximum_price and v.crossout = false"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Проверить, что в оффере нет поля oldprice"):
                check.equal("oldprice" not in feed_offer[0], True, "Oldprice should not be present")

            with allure.step("Проверить, что в оффере есть поле price и в него передается значение current_price"):
                current_price = self.entity_by_id(table="variations", id=variation_id)["current_price"]
                check.equal(feed_offer[0]["price"], str(current_price), "Price mismatch")

            with allure.step("Проверить, что в оффере нет параметра  Скидка"):
                discount_param = list(
                    filter(
                        lambda param: param["@name"] == helpers.code_unicode("Скидка"),
                        feed_offer[0]["param"],
                    )
                )
                check.equal(len(discount_param), 0, "Discount param should not be present")

            with allure.step(
                "Найти в базе товар, у которого current_price != maximum_price и параметр crossout = True"
            ):
                conditions = ["and v.current_price != v.maximum_price and v.crossout = true"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Проверить, что в оффере есть поле oldprice и в него передается значение maximum_price"):
                maximum_price = self.entity_by_id(table="variations", id=variation_id)["maximum_price"]
                check.equal(feed_offer[0]["oldprice"], str(maximum_price), "Oldprice mismatch")

            with allure.step("Проверить, что в оффере есть поле price и в него передается значение current_price"):
                current_price = self.entity_by_id(table="variations", id=variation_id)["current_price"]
                check.equal(feed_offer[0]["price"], str(current_price), "Price mismatch")

        with allure.step("Проверить формирование поля url"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в оффере есть поле url"):
                check.equal("url" in random_offer, True, "Url should be present")

            with allure.step("Найти в базе вариант продукта по id из рандомного офера"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["@id"])

            with allure.step("Найти в базе продукт по id товара"):
                product_data = self.entity_by_id(table="products", id=random_offer["@group_id"])

            with allure.step("Проверить, что в оффере url соответствует url продукта"):
                gender = "zhenskaya" if product_data["gender"] == "female" else "muzhskaya"
                url = (
                    f"{os.getenv('SHOP_URL')}/{gender}/product/{product_data['article']}/{variation_data['color_code_id']}?size={variation_data['size_id']}&height={variation_data['height_id']}"
                    if variation_data["height_id"]
                    else f"{os.getenv('SHOP_URL')}/{gender}/product/{product_data['article']}/{variation_data['color_code_id']}?size={variation_data['size_id']}&height="
                )
                check.equal(random_offer["url"], url, "Url mismatch")

        with allure.step("Проверить значение категории в офере"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти в базе продукт по id варианта"):
                product_data = self.entity_by_id(table="products", id=random_offer["@group_id"])

            with allure.step("Проверить, что в офере значение категории соответствует значению категории в продукте"):
                check.equal(
                    random_offer["categoryId"],
                    str(product_data["category_id"]),
                    "Category id mismatch",
                )

        with allure.step("Проверить формирование поля currency"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле currencyId и равно RUB"):
                check.equal("currencyId" in random_offer, True, "Currency id should be present")
                check.equal(random_offer["currencyId"], "RUB", "Currency id should be RUB")

        with allure.step("Проверить формирование поля vendor"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле vendor и равно befree"):
                check.equal("vendor" in random_offer, True, "Vendor should be present")
                check.equal(random_offer["vendor"], "befree", "Vendor should be befree")

        with allure.step("Проверить формирование поля name, model и typePrefix"):
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
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_id), offers))

            with allure.step("Проверить, что в офере есть поле name и model"):
                check.equal("name" in feed_offer[0], True, "Name should be present")
                check.equal("model" in feed_offer[0], True, "Model should be present")

            with allure.step("Проверить, что в офере name  и model соответствует наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["name"]),
                    product_data["title"].capitalize(),
                    "Name mismatch",
                )
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["model"]),
                    product_data["title"],
                    "Model mismatch",
                )

                check.equal(
                    helpers.decode_unicode(feed_offer[0]["typePrefix"]),
                    product_data["title"],
                    "TypePrefix mismatch",
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
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_id), offers))

            with allure.step("Проверить, что в офере есть поле name и model"):
                check.equal("name" in feed_offer[0], True, "Name should be present")
                check.equal("model" in feed_offer[0], True, "Model should be present")

            with allure.step("Проверить, что в офере name соответствует маркетинговому наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["name"]),
                    product_data["marketing_title"].capitalize(),
                    "Name mismatch",
                )
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["model"]),
                    product_data["marketing_title"],
                    "Model mismatch",
                )

                check.equal(
                    helpers.decode_unicode(feed_offer[0]["typePrefix"]),
                    product_data["title"],
                    "TypePrefix mismatch",
                )

        with allure.step("Проверить формирование поля barcode и vendorCode"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти в базе вариант продукта по id из рандомного офера"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["@id"])

            with allure.step("Проверить, что в офере есть поле barcode и vendorCode и равно sku варианта"):
                check.equal("barcode" in random_offer, True, "Barcode should be present")
                check.equal(random_offer["barcode"], variation_data["sku"], "Barcode mismatch")

                check.equal("vendorCode" in random_offer, True, "VendorCode should be present")
                check.equal(random_offer["vendorCode"], variation_data["sku"], "VendorCode mismatch")

        with allure.step("Проверить наличие поля description"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле description"):
                check.equal("description" in random_offer, True, "Description should be present")

        with allure.step("Проверить наличие поля country_of_origin"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле country_of_origin"):
                check.equal("country_of_origin" in random_offer, True, "Country of origin should be present")

        with allure.step("Проверить формирование поля delivery"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле delivery и равно true"):
                check.equal("delivery" in random_offer, True, "Delivery should be present")
                check.equal(random_offer["delivery"], "true", "Delivery should be true")

        with allure.step("Проверить наличие в фиде определенных атрибутов продуктов"):
            params = [
                "Артикул",
                "Цвет",
                "Код цвета",
                "Размер",
                "Пол",
                "Рост",
            ]
            for param in params:
                with allure.step(f"Проверить, что в фиде есть параметр {param}"):
                    param_name = helpers.code_unicode(param)
                    feed_offer = list(
                        filter(
                            lambda item: list(filter(lambda param: param["@name"] == param_name, item["param"])),
                            offers,
                        )
                    )
                    check.greater(len(feed_offer), 0, f"Param {param} should be present")
