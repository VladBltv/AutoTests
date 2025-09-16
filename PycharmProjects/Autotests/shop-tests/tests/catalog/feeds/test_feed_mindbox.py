import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
import random
import os
from utils import helpers
from pytest_check import check


class TestFeedMindbox(QueriesCatalog):
    @allure.id("572")
    @allure.title("Фид mindbox: категории и оферы")
    @allure.label("service", "Catalog")
    @allure.feature("Mindbox", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """Требования к формированию фида

        В секции categories записываются все сущности компиляций с параметром is_category = true
        В секции categories не помещаются сущности компиляций, которые имеют параметр is_category = false
        Для наполнения offers должны выполняться следующие условия
        Остатки на fulfilment > 1 (inventories - fulfilment)
        Вариант не удален: deleted_at is null
        Товар не находится в заморозке: "fulfilment_frozen"=false
        Консольная команда для генерации фида: php artisan befree:generate_feed mindbox
        Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/mindbox.xml
        Дока https://confluence.melonfashion.ru/pages/viewpage.action?pageId=1099989687
        """
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_mindbox_categories_and_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed mindbox"""
                pass
        with allure.step("Запросить фид"):
            feed_mindbox: Response = api.storage_session.get("/storage/feeds/mindbox.xml")
            assert feed_mindbox.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/mindbox.xml"), feed_mindbox.text)
            files.xml_to_json(files.generate_absolute_path("resources/mindbox.xml"), "mindbox")

            mindbox_feed_data = json.loads(files.read(files.generate_absolute_path("resources/mindbox.json")))

        with allure.step("Сформировать в базе список актуальных id категорий"):
            query = """
                    select c.id
                    from compilations c 
                    where c.deleted_at is null and c.is_category is true
                """

            categories_base = list(map(lambda n: n["id"], db_connection.catalog.get_data(query)))

            with allure.step("Список должен совпадать со списком категорий в фиде"):
                categories_feed = list(
                    map(
                        lambda n: int(n["@id"]),
                        mindbox_feed_data["yml_catalog"]["shop"]["categories"]["category"],
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
                        mindbox_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                    )
                )
                assert len(list(set(offers_base) ^ set(offers_feed))) == 0

    @allure.id("2561")
    @allure.title("Фид mindbox: структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Mindbox", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe mindbox")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_mindbox_data_structure(self):
        with allure.step("Минимальное количество по ff/omni"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            min_qty_omni = os.getenv("MIN_QTY_OMNI")
        with allure.step("Запросить фид"):
            feed_mindbox: Response = api.storage_session.get("/storage/feeds/mindbox.xml")
            assert feed_mindbox.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/mindbox.xml"), feed_mindbox.text)
            files.xml_to_json(files.generate_absolute_path("resources/mindbox.xml"), "mindbox")

            mindbox_feed_data = json.loads(files.read(files.generate_absolute_path("resources/mindbox.json")))

            offers = mindbox_feed_data["yml_catalog"]["shop"]["offers"]["offer"]

        with allure.step("Проверить, что в поле @group_id соответстует id продукта"):
            with allure.step("Взять рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Получить данные по варианту"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["@id"])

            with allure.step("Проверить, что в поле @group_id соответстует id продукта"):
                check.equal(
                    random_offer["@group_id"],
                    str(variation_data["product_id"]),
                    "group_id should be equal to product_id",
                )

        with allure.step("Проверить, что в поле @available равно true у всех оферов"):
            not_available_offers = list(
                filter(
                    lambda item: item["@available"] == "false",
                    offers,
                )
            )
            check.equal(len(not_available_offers), 0, "not_available_offers should be empty")

        with allure.step("Проверить формирование поля url"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в оффере есть поле url"):
                check.equal("url" in random_offer, True, "Url should be present")

            with allure.step("Найти в базе вариант продукта по id из рандомного офера"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["@id"])

            with allure.step("Найти в базе продукт по id варианта"):
                product_data = self.entity_by_id(table="products", id=random_offer["@group_id"])

            with allure.step("Проверить, что в оффере url соответствует url продукта"):
                gender = "zhenskaya" if product_data["gender"] == "female" else "muzhskaya"
                url = (
                    f"{os.getenv('SHOP_URL')}/{gender}/product/{product_data['article']}/{variation_data['color_code_id']}?size={variation_data['size_id']}&height={variation_data['height_id']}"
                    if variation_data["height_id"]
                    else f"{os.getenv('SHOP_URL')}/{gender}/product/{product_data['article']}/{variation_data['color_code_id']}?size={variation_data['size_id']}&height="
                )
                check.equal(random_offer["url"], url, "Url mismatch")

        with allure.step("Проверить формирования полей price и oldprice"):
            with allure.step("Найти в базе товар, у которого current_price == maximum_price"):
                conditions = ["and v.current_price = v.maximum_price"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Проверить, что в оффере нет поля oldprice"):
                check.equal("oldprice" not in feed_offer[0], True, "Oldprice should not be present")

            with allure.step("Проверить, что в оффере есть поле price и в него передается значение current_price"):
                current_price = self.entity_by_id(table="variations", id=variation_id)["current_price"]
                check.equal(feed_offer[0]["price"], str(current_price), "Price mismatch")

            with allure.step(
                "Найти в базе товар, у которого current_price != maximum_price и параметр crossout = False"
            ):
                conditions = ["and v.current_price != v.maximum_price and v.crossout = false"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Проверить, что в оффере нет поля oldprice"):
                check.equal("oldprice" not in feed_offer[0], True, "Oldprice should not be present")

            with allure.step("Проверить, что в оффере есть поле price и в него передается значение current_price"):
                current_price = self.entity_by_id(table="variations", id=variation_id)["current_price"]
                check.equal(feed_offer[0]["price"], str(current_price), "Price mismatch")

            with allure.step(
                "Найти в базе товар, у которого current_price != maximum_price и параметр crossout = True"
            ):
                conditions = ["and v.current_price != v.maximum_price and v.crossout = true"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_id = offers_base[0]["variation_id"]
                feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

            with allure.step("Проверить, что в оффере есть поле oldprice и в него передается значение maximum_price"):
                maximum_price = self.entity_by_id(table="variations", id=variation_id)["maximum_price"]
                check.equal(feed_offer[0]["oldprice"], str(maximum_price), "Oldprice mismatch")

            with allure.step("Проверить, что в оффере есть поле price и в него передается значение current_price"):
                current_price = self.entity_by_id(table="variations", id=variation_id)["current_price"]
                check.equal(feed_offer[0]["price"], str(current_price), "Price mismatch")

        with allure.step("Проверить значение категории в офере"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти в базе продукт по id товара"):
                product_data = self.entity_by_id(table="products", id=random_offer["@group_id"])

            with allure.step("Проверить, что в офере значение категории соответствует значению категории в продукте"):
                check.equal(
                    random_offer["categoryId"],
                    str(product_data["category_id"]),
                    "Category id mismatch",
                )

        with allure.step("Проверить формирование поля vendor"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле vendor и равно befree"):
                check.equal("vendor" in random_offer, True, "Vendor should be present")
                check.equal(random_offer["vendor"], "befree", "Vendor should be befree")

        with allure.step("Проверить формирование поля model"):
            with allure.step("Найти в базе продукт без маркетингового названия"):
                conditions = ["p.marketing_title is null and p.fulfilment_qty > 0"]
                product_id = self.get_product_by_conditions(conditions=conditions)["id"]
                product_data = self.entity_by_id(table="products", id=product_id)

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_id), offers))

            with allure.step("Проверить, что в офере есть поле model"):
                check.equal("model" in feed_offer[0], True, "Name should be present")

            with allure.step("Проверить, что в офере model соответствует наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["model"]),
                    product_data["title"],
                    "Name mismatch",
                )

            with allure.step("Найти в базе продукт c маркетинговым наименованием"):
                conditions = ["p.marketing_title is not null and p.fulfilment_qty > 0"]
                product_id = self.get_product_by_conditions(conditions=conditions)["id"]
                product_data = self.entity_by_id(table="products", id=product_id)

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_id), offers))

            with allure.step("Проверить, что в офере есть поле model"):
                check.equal("model" in feed_offer[0], True, "Name should be present")

            with allure.step("Проверить, что в офере model соответствует маркетинговому наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["model"]),
                    product_data["marketing_title"].capitalize(),
                    "Model mismatch",
                )

        with allure.step("Проверить формирование поля vendorCode"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти в базе продукт по id товара"):
                product_data = self.entity_by_id(table="products", id=random_offer["@group_id"])

            with allure.step("Проверить, что в офере есть поле vendorCode и равно артикулу продукта"):
                check.equal("vendorCode" in random_offer, True, "VendorCode should be present")
                check.equal(random_offer["vendorCode"], product_data["article"], "VendorCode mismatch")

        with allure.step("Проверить формирование поля barcodebefree"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти в базе вариант продукта по id из рандомного офера"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["@id"])

            with allure.step("Проверить, что в офере есть поле barcode и равно sku варианта"):
                check.equal("barcodebefree" in random_offer, True, "barcodebefree should be present")
                check.equal(random_offer["barcodebefree"], variation_data["sku"], "barcodebefree mismatch")

        with allure.step("Проверить наличие в фиде определенных атрибутов продуктов"):
            params = [
                "Цвет",
                "Код цвета",
                "Размер",
                "Пол",
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
