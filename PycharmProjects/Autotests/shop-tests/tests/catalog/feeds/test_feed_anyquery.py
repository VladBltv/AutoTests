import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files, helpers
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
import random
import os
from pytest_check import check
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TestFeedAnyquery(QueriesCatalog):
    @allure.id("2546")
    @allure.title("Фид anyquery: категории и оферы")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.description(
        """
            Требования к формированию фида
    
            В секции categories записываются все сущности компиляций с параметром is_category = true
            В секции categories не помещаются сущности компиляций, которые имеют параметр is_category = false
            Для наполнения offers должны выполняться следующие условия
            Товар не в заморозке или по складу fulfilment или по складу omni
            Товар не помечен на удаление
            Цена не равна 0
            Остаток товара не важен
            Не добавляются варианты созданные раньше 2024-04-08
            Не добавляются варианты у которых нет остатка и дата inventory_updated_at  больше 6 мес
            Консольная команда для генерации фида: php artisan befree:generate_feed anyquery
            Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/anyquery.xml
            
            Дока https://confluence.melonfashion.ru/pages/viewpage.action?pageId=1121657921
        """
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_anyquery_categories_and_offers(self):
        with allure.step("Генерация фида проходит успешно"):
            # Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed anyquery
            pass
        with allure.step("Запросить фид"):
            feed_anyquery: Response = api.storage_session.get("/storage/feeds/anyquery.xml")
            check.equal(feed_anyquery.status_code, 200, "Feed request should return 200 status code")

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/anyquery.xml"), feed_anyquery.text)
            files.xml_to_json(files.generate_absolute_path("resources/anyquery.xml"), "anyquery")

            anyquery_feed_data = json.loads(files.read(files.generate_absolute_path("resources/anyquery.json")))

        with allure.step("Сформировать в базе список актуальных id категорий"):
            categories_base = list(map(lambda n: n["id"], self.get_active_categories()))

        with allure.step("Список должен совпадать со списком категорий в фиде"):
            categories_feed = list(
                map(
                    lambda n: int(n["@id"]),
                    anyquery_feed_data["yml_catalog"]["shop"]["categories"]["category"],
                )
            )
            # Расхождение в 2 штуки, потому что в фид anyquery добавляются две фантомные категории М и Ж
            check.equal(
                len(list(set(categories_base) ^ set(categories_feed))),
                2,
                "Categories count mismatch",
            )

        with allure.step("Сформировать в базе список вариантов подпадающих под условия отбора в фида"):
            query_all = """
                    select v.id
                    from variations as v 
                    join products as p on v.product_id=p.id 
                    where 
                        v.current_price != 0 
                        and v.deleted_at is null 
                        and (p.fulfilment_frozen is false or p.omni_frozen is false or p.omni2_frozen is false or p.sfs_frozen is false)
                """

            offers_base_all = list(map(lambda n: n["id"], db_connection.catalog.get_data(query_all)))

            query_old_created = """
                select v.id
                from variations as v 
                join products as p on v.product_id = p.id 
                where 
                    v.current_price != 0 
                    and v.deleted_at is null 
                    and (p.fulfilment_frozen is false or p.omni_frozen is false or p.omni2_frozen is false or p.sfs_frozen is false)
                    and v.created_at  < '2024-04-08 00:00:00.000'
                    and not exists (
                        select  pi2.variation_id 
                        from product_inventories pi2
                        where pi2.variation_id = v.id and pi2.qty > 0
                    )
            """

            current_date = datetime.now()
            six_months_ago = (current_date - relativedelta(months=6)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            query_old_updated = f"""
                select v.id
                from variations as v 
                join products as p on v.product_id = p.id 
                where 
                    v.current_price != 0 
                    and v.deleted_at is null 
                    and (p.fulfilment_frozen is false or p.omni_frozen is false or p.omni2_frozen is false or p.sfs_frozen is false)
                    and v.inventory_updated_at is not null and v.inventory_updated_at  < '{six_months_ago}'
                    and not exists (
                        select  pi2.variation_id 
                        from product_inventories pi2
                        where pi2.variation_id = v.id and pi2.qty > 0
                    )
            """

            offers_base_old_created = list(map(lambda n: n["id"], db_connection.catalog.get_data(query_old_created)))
            offers_base_old_updated = list(map(lambda n: n["id"], db_connection.catalog.get_data(query_old_updated)))

            offers_base = list(set(offers_base_all) - set(offers_base_old_created) - set(offers_base_old_updated))

        with allure.step("Варианты из списка совпадают с вариантами в фиде"):
            offers_feed = list(
                map(
                    lambda n: int(n["@id"]),
                    anyquery_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                )
            )
            offers_base_not_in_feed = list(set(offers_base) - set(offers_feed))
            print("offers_base_not_in_feed", offers_base_not_in_feed)
            offers_feed_not_in_base = list(set(offers_feed) - set(offers_base))
            print("offers_feed_not_in_base", offers_feed_not_in_base)

            check.equal(len(offers_base_not_in_feed), 0, "Offers base not in feed exist")
            check.equal(len(offers_feed_not_in_base), 0, "Offers feed not in base exist")

    @allure.id("2547")
    @allure.title("Фид anyquery проверка поля available")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование значения поля available в фиде anyquery")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_anyquery_validate_availablity(self):
        with allure.step("Минимальное количество по ff/omni"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            min_qty_omni = os.getenv("MIN_QTY_OMNI")
        with allure.step("Запросить фид"):
            feed_anyquery: Response = api.storage_session.get("/storage/feeds/anyquery.xml")
            check.equal(feed_anyquery.status_code, 200, "Feed request should return 200 status code")

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/anyquery.xml"), feed_anyquery.text)
            files.xml_to_json(files.generate_absolute_path("resources/anyquery.xml"), "anyquery")

            anyquery_feed_data = json.loads(files.read(files.generate_absolute_path("resources/anyquery.json")))

            offers = anyquery_feed_data["yml_catalog"]["shop"]["offers"]["offer"]

        with allure.step("Найти товар, который не заморожен, не удален, цена не 0, нет в наличии ни на одном складе"):
            conditions = ["and v.created_at > '2024-04-08 00:00:00.000'"]
            offers_base = self.find_variation_by_availability_condition(qty_ff=None, qty_omni=None, conditions=conditions)
            variation_id = offers_base[0]["variation_id"]
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

        with allure.step("Проверить, что параметр available=false"):
            check.equal(feed_offer[0]["@available"], "false", variation_id)

        with allure.step(
            f"Найти товар, который не заморожен, не удален, цена не 0, в наличии только на складе ff в количестве больше или равно трешхолда {min_qty_ff}"
        ):
            offers_base = self.find_variation_by_availability_condition(qty_ff=f">= {min_qty_ff}", qty_omni=None)
            variation_id = offers_base[0]["variation_id"]
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

        with allure.step("Проверить, что параметр available=true"):
            check.equal(feed_offer[0]["@available"], "true", variation_id)

        with allure.step(
            f"Найти товар, который не заморожен, не удален, цена не 0, в наличии только на складе омни в количестве большем или равным трешхолду {min_qty_omni}"
        ):
            offers_base = self.find_variation_by_availability_condition(qty_ff=None, qty_omni=f">= {min_qty_omni}")
            variation_id = offers_base[0]["variation_id"]
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

        with allure.step("Проверить, что параметр available=true"):
            check.equal(feed_offer[0]["@available"], "true", variation_id)

        with allure.step(
            f"Найти товар, который не заморожен, не удален, цена не 0, в наличии на обоих типах складов в количестве большем или равным трешхолду {min_qty_ff} / {min_qty_omni}"
        ):
            offers_base = self.find_variation_by_availability_condition(
                qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}"
            )
            variation_id = offers_base[0]["variation_id"]
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

        with allure.step("Проверить, что параметр available=true"):
            check.equal(feed_offer[0]["@available"], "true", variation_id)

        with allure.step("Найти товар, который заморожен только по ff и есть в наличии только в ff"):
            offers_base = self.find_variation_by_availability_condition(
                qty_ff=f">= {min_qty_ff}", qty_omni=None, ff_frozen=True
            )
            variation_id = offers_base[0]["variation_id"]
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

        with allure.step("Проверить, что параметр available=false"):
            check.equal(feed_offer[0]["@available"], "false", variation_id)

        with allure.step("Найти товар, который заморожен только по онми и есть в наличии только в онми"):
            offers_base = self.find_variation_by_availability_condition(
                qty_ff=None, qty_omni=f">= {min_qty_omni}", omni_frozen=True
            )
            variation_id = offers_base[0]["variation_id"]
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))

        with allure.step("Проверить, что параметр available=false"):
            check.equal(feed_offer[0]["@available"], "false", variation_id)

    @allure.id("2548")
    @allure.title("Фид anyquery структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование отдельных полей в структуре офера в фиде anyquery")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_anyquery_data_structure(self):
        with allure.step("Минимальное количество по ff"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            min_qty_omni = os.getenv("MIN_QTY_OMNI")
        with allure.step("Запросить фид"):
            feed_anyquery: Response = api.storage_session.get("/storage/feeds/anyquery.xml")
            check.equal(feed_anyquery.status_code, 200, "Feed request should return 200 status code")

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/anyquery.xml"), feed_anyquery.text)
            files.xml_to_json(files.generate_absolute_path("resources/anyquery.xml"), "anyquery")

            anyquery_feed_data = json.loads(files.read(files.generate_absolute_path("resources/anyquery.json")))
            offers = anyquery_feed_data["yml_catalog"]["shop"]["offers"]["offer"]

        with allure.step("Проверить, что в поле @group_id соответстует id продукта"):
            with allure.step("Найти в базе товар с обоих складов"):
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}"
                )
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
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
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
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
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

            with allure.step(
                "Проверить, что в оффере есть параметр Скидка и в него передается значение скидки варианта"
            ):
                discount_param = list(
                    filter(
                        lambda param: param["@name"] == helpers.code_unicode("Скидка"),
                        feed_offer[0]["param"],
                    )
                )
                check.equal(len(discount_param), 1, "Discount param should be present")
                variation_data = self.entity_by_id(table="variations", id=variation_id)
                check.equal(
                    discount_param[0]["#text"],
                    str(variation_data["discount_percent_level_0"]),
                    "Discount mismatch",
                )

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

            with allure.step("Проверить, что в офере есть поле currencyId и равно RUR"):
                check.equal("currencyId" in random_offer, True, "Currency id should be present")
                check.equal(random_offer["currencyId"], "RUR", "Currency id should be RUR")

        with allure.step("Проверить формирование поля vendor"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле vendor и равно befree"):
                check.equal("vendor" in random_offer, True, "Vendor should be present")
                check.equal(random_offer["vendor"], "befree", "Vendor should be befree")

        with allure.step("Проверить формирование поля barcode"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Найти в базе вариант продукта по id из рандомного офера"):
                variation_data = self.entity_by_id(table="variations", id=random_offer["@id"])

            with allure.step("Проверить, что в офере есть поле barcode и равно sku варианта"):
                check.equal("barcode" in random_offer, True, "Barcode should be present")
                check.equal(random_offer["barcode"], variation_data["sku"], "Barcode mismatch")

        with allure.step("Проверить формирование поля name"):
            with allure.step("Найти продукт без маркетингового названия"):
                conditions = ["and p.marketing_title is null"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                product_data = self.entity_by_id(table="products", id=variation_data["product_id"])

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_data["id"]), offers))

            with allure.step("Проверить, что в офере есть поле name"):
                check.equal("name" in feed_offer[0], True, "Name should be present")

            with allure.step("Проверить, что в офере name соответствует наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["name"]),
                    product_data["title"].capitalize(),
                    "Name mismatch",
                )

            with allure.step("Найти в базе продукт c маркетинговым наименованием"):
                conditions = ["and p.marketing_title is not null"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                product_data = self.entity_by_id(table="products", id=variation_data["product_id"])

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_data["id"]), offers))

            with allure.step("Проверить, что в офере есть поле name"):
                check.equal("name" in feed_offer[0], True, "Name should be present")

            with allure.step("Проверить, что в офере name соответствует маркетинговому наименованию продукта"):
                check.equal(
                    helpers.decode_unicode(feed_offer[0]["name"]),
                    product_data["marketing_title"].capitalize(),
                    "Name mismatch",
                )
        with allure.step("Проверить формирование поля Пол"):
            with allure.step("Найти в базе продукт с полом male"):
                conditions = ["and p.gender = 'male'"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                product_data = self.entity_by_id(table="products", id=variation_data["product_id"])

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_data["id"]), offers))

            with allure.step("Проверить, что в офере Пол соответствует значению пола в продукте"):
                gender_param = list(
                    filter(
                        lambda param: param["@name"] == helpers.code_unicode("Пол"),
                        feed_offer[0]["param"],
                    )
                )
                check.equal(gender_param[0]["#text"], helpers.code_unicode("мужской"), "Gender mismatch")

            with allure.step("Найти в базе продукт с полом female"):
                conditions = ["and p.gender = 'female'"]
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", conditions=conditions
                )
                variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                product_data = self.entity_by_id(table="products", id=variation_data["product_id"])

            with allure.step("Найти в фиде товар по id продукта"):
                feed_offer = list(filter(lambda item: item["@group_id"] == str(product_data["id"]), offers))

            with allure.step("Проверить, что в офере Пол соответствует значению пола в продукте"):
                gender_param = list(
                    filter(
                        lambda param: param["@name"] == helpers.code_unicode("Пол"),
                        feed_offer[0]["param"],
                    )
                )
                check.equal(gender_param[0]["#text"], helpers.code_unicode("женский"), "Gender mismatch")

        with allure.step("Проверить наличие в фиде определенных атрибутов продуктов"):
            # "Модель пижамы"
            params = [
                "Артикул",
                "Цвет",
                "Код цвета",
                "Размер",
                "Пол",
                "Рост",
                "Тип изделия",
                "Стиль",
                "Модель ботинок",
                "Модель брюк",
                "Модель босоножек",
                "Модель джинс",
                "Модель комбинезона",
                "Модель купальника",
                "Модель трусов",
                "Модель шапки",
                "Модель юбки",
                "Вид бюстгальтера",
                "Тип сумки",
                "Тип платья",
                "Тип рубашки",
                "Тип джинс (укороченные)",
                "Длина",
                "Длина платья",
                "Длина юбки",
                "Рукава",
                "Посадка",
                "Талия",
                "Вид бретелей",
                "Вид застежки",
                "Вид каблука",
                "Вид шляпы",
                "Вырез",
                "Вырез горловины",
                "Оттенок",
                "Материал",
                "Материал (деним)",
                "Материал тренча",
                "Фактура",
                "Фактура материала",
                "Принт",
                "Вязка",
                "Капюшон",
                "Наличие чашки",
                "Опции опушки",
                "Особенности белья",
                "Особенности модели",
                "Особенности ремня",
                "Особенности сумки",
                "Утеплитель",
                "Чашка",
                "Сезон",
                "Новинка",
                "Скидка",
                "Линия",
                "Вид украшения",
                "Высота обуви",
                "Карманы",
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

        with allure.step("Проверить, что в фиде нет атрибута Описанние"):
            param_name = helpers.code_unicode("Описание")
            feed_offer = list(
                filter(
                    lambda item: list(filter(lambda param: param["@name"] == param_name, item["param"])),
                    offers,
                )
            )
            check.equal(len(feed_offer), 0, "Description param should not be present")
