import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files, helpers
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from pytest_check import check
import random
from voluptuous import PREVENT_EXTRA, Schema
from pytest_voluptuous import S
import os


class TestFeedAnyqueryCityFF(QueriesCatalog):
    @allure.id("2551")
    @allure.title("Региональный фид anyquery fulfilment: категории и оферы")
    @allure.severity(Severity.CRITICAL)
    @allure.tag("critical")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """
            Требования к формированию фида
    
            В секции categories записываются все сущности компиляций с параметром is_category = true
            В секции categories не помещаются сущности компиляций, которые имеют параметр is_category = false
            Для наполнения offers должны выполняться следующие условия
            Товар не в заморозке по складу fulfilment
            Товар не помечен на удаление
            Цена не равна 0
            Товар в наличии на складе fulfilment 
            Консольная команда для генерации фида: php artisan befree:generate_feed anyquery_city
            Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/cities/fulfilment.xml
            
            Дока https://confluence.melonfashion.ru/pages/viewpage.action?pageId=1164053257
        """
    )
    def test_feed_anyquery_city_fulfilment_categories_and_offers(self):
        with allure.step("Генерация фида проходит успешно"):
            # Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed anyquery_city
            pass
        with allure.step("Запросить фид"):
            feed_anyquery_city: Response = api.storage_session.get("/storage/feeds/cities/fulfilment.xml")
            check.equal(feed_anyquery_city.status_code, 200, "Feed request should return 200 status code")

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(
                files.generate_absolute_path("resources/anyquery_fulfilment.xml"),
                feed_anyquery_city.text,
            )
            files.xml_to_json(
                files.generate_absolute_path("resources/anyquery_fulfilment.xml"),
                "anyquery_fulfilment",
            )

            anyquery_feed_data = json.loads(
                files.read(files.generate_absolute_path("resources/anyquery_fulfilment.json"))
            )

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
            query = """
                    select distinct v.id
                    from variations as v 
                    left join products as p on v.product_id=p.id 
                    left join product_inventories pi2 on pi2.variation_id = v.id
                    where 
                        v.current_price != 0 
                        and v.deleted_at is null 
                        and (p.fulfilment_frozen is false or p.omni_frozen is false or p.omni2_frozen is false or p.sfs_frozen is false)
                        and v.fulfilment_qty > 0
                """

            offers_base = list(map(lambda n: n["id"], db_connection.catalog.get_data(query)))

        with allure.step("Варианты из списка совпадают с вариантами в фиде"):
            offers_feed = list(
                map(
                    lambda n: int(n["@id"]),
                    anyquery_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                )
            )

            offers_base_not_in_feed = list(set(offers_base) - set(offers_feed))
            print(offers_base_not_in_feed)
            offers_feed_not_in_base = list(set(offers_feed) - set(offers_base))
            print(offers_feed_not_in_base)
            offers_diff = list(set(offers_base) ^ set(offers_feed))
            check.equal(len(offers_base_not_in_feed), 0, "Offers should match between feed and database")
            check.equal(len(offers_feed_not_in_base), 0, "Offers should match between feed and database")
            check.equal(len(offers_diff), 0, "Offers should match between feed and database")

    @allure.id("2553")
    @allure.severity(Severity.CRITICAL)
    @allure.title("Региональный фид anyquery: признак available")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """Проверяем корректно формирование признака available в фиде anyquery для fulfilment
                        available = true - товар имеет остаток по ff больше трешхолда и не заморожен по ff
                        available = false - в остальных случаях
                        """
    )
    def test_feed_anyquery_city_fulfilment_offers_validate_availablity(self):
        with allure.step("Минимальное количество по ff/omni"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            min_qty_omni = os.getenv("MIN_QTY_OMNI")
        with allure.step("Запросить фид"):
            feed_anyquery_city: Response = api.storage_session.get("/storage/feeds/cities/fulfilment.xml")
        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(
                files.generate_absolute_path("resources/anyquery_fulfilment.xml"), feed_anyquery_city.text
            )
            files.xml_to_json(
                files.generate_absolute_path("resources/anyquery_fulfilment.xml"),
                "anyquery_fulfilment",
            )

            anyquery_feed_data = json.loads(
                files.read(files.generate_absolute_path("resources/anyquery_fulfilment.json"))
            )

            offers = anyquery_feed_data["yml_catalog"]["shop"]["offers"]["offer"]

        with allure.step("Найти в базе товар, который заморожен по всем складам, но есть остаток по ff"):
            offers_base = self.find_variation_by_availability_condition(
                ff_frozen=True,
                omni_frozen=True,
                omni2_frozen=True,
                sfs_frozen=True,
                qty_ff=f">= {min_qty_ff}",
            )
            variation_id = offers_base[0]["variation_id"]

        with allure.step("Проверить, что в фиде нет этого товара"):
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))
            check.equal(len(feed_offer), 0, "Feed offer should not be present")

        with allure.step("Найти в базе товар, который есть в наличии только в фф"):
            offers_base = self.find_variation_by_availability_condition(qty_ff=f">= {min_qty_ff}", qty_omni=None)
            variation_id = offers_base[0]["variation_id"]

        with allure.step("Проверить, что в фиде есть этот товар"):
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))
            check.equal(len(feed_offer), 1, "Feed offer should be present")
            check.equal(feed_offer[0]["@available"], "true", "Feed offer should be available")

        with allure.step("Найти в базе товар, который есть в наличии только в омни"):
            offers_base = self.find_variation_by_availability_condition(qty_ff=None, qty_omni=f">= {min_qty_omni}")
            variation_id = offers_base[0]["variation_id"]

        with allure.step("Проверить, что в фиде нет этого товара"):
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))
            check.equal(len(feed_offer), 0, "Feed offer should not be present")

        with allure.step("Найти в базе товар, который заморожен только по ff и есть в наличии только в ff"):
            offers_base = self.find_variation_by_availability_condition(
                ff_frozen=True, qty_ff=f">= {min_qty_ff}", qty_omni=None
            )
            variation_id = offers_base[0]["variation_id"]

        with allure.step("Проверить, что в фиде есть этот товар"):
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))
            check.equal(len(feed_offer), 1, "Feed offer should be present")
            check.equal(feed_offer[0]["@available"], "false", "Feed offer should not be available")

        with allure.step(
            "Найти в базе товар, который заморожен по ff и есть остаток по ff но активен в омни и есть наличие в омни"
        ):
            offers_base = self.find_variation_by_availability_condition(
                ff_frozen=True, qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", city_id_in=2
            )
            variation_id = offers_base[0]["variation_id"]

        with allure.step("Проверить, что в фиде есть этот товар"):
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))
            check.equal(len(feed_offer), 1, "Feed offer should be present")
            check.equal(feed_offer[0]["@available"], "false", "Feed offer should not be available")

        with allure.step(
            "Найти в базе товар, который заморожен по омни есть остаток по омни, но активен по ff и есть наличие по ff"
        ):
            offers_base = self.find_variation_by_availability_condition(
                omni_frozen=True, qty_omni=f">= {min_qty_omni}", qty_ff=f">= {min_qty_ff}", city_id_in=2
            )
            variation_id = offers_base[0]["variation_id"]

        with allure.step("Проверить, что в фиде есть этот товар"):
            feed_offer = list(filter(lambda item: item["@id"] == str(variation_id), offers))
            check.equal(len(feed_offer), 1, "Feed offer should be present")
            check.equal(feed_offer[0]["@available"], "true", "Feed offer should be available")

    @allure.id("2554")
    @allure.title("Фид anyquery для города структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        "Проверяем корректное формирование отдельных полей в структуре офера в фиде anyquery_fulfilment"
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_anyquery_city_fulfilment_data_structure(self):
        with allure.step("Минимальное количество по ff/omni"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            min_qty_omni = os.getenv("MIN_QTY_OMNI")
        with allure.step("Запросить фид"):
            feed_anyquery_city: Response = api.storage_session.get("/storage/feeds/cities/fulfilment.xml")
        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(
                files.generate_absolute_path("resources/anyquery_fulfilment.xml"),
                feed_anyquery_city.text,
            )
            files.xml_to_json(
                files.generate_absolute_path("resources/anyquery_fulfilment.xml"),
                "anyquery_fulfilment",
            )

            anyquery_feed_data = json.loads(
                files.read(files.generate_absolute_path("resources/anyquery_fulfilment.json"))
            )

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
                check.equal("param" not in feed_offer[0], True, "Discount param should not be present")

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
                check.equal("param" not in feed_offer[0], True, "Discount param should not be present")

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
                check.equal(
                    feed_offer[0]["param"]["@name"],
                    helpers.code_unicode("Скидка"),
                    "Discount param should be present",
                )
                variation_data = self.entity_by_id(table="variations", id=variation_id)
                check.equal(
                    feed_offer[0]["param"]["#text"],
                    str(variation_data["discount_percent_level_0"]),
                    "Discount mismatch",
                )
        with allure.step("Проверить формирование поля currency"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть поле currencyId и равно RUR"):
                check.equal("currencyId" in random_offer, True, "Currency id should be present")
                check.equal(random_offer["currencyId"], "RUR", "Currency id should be RUR")

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
        with allure.step("Проверить схему полей в офере"):
            with allure.step("Взять из фида рандомный офер"):
                random_offer = random.choice(offers)

            with allure.step("Проверить, что в офере есть все обязательные поля"):
                offer_schema = Schema(
                    {
                        "@id": str,  # обязательное поле
                        "@group_id": str,  # обязательное поле
                        "@available": str,  # обязательное поле
                        "@type": "vendor.model",  # обязательное поле
                        "oldprice": str,  # не обязательное поле
                        "price": str,  # обязательное поле
                        "categoryId": str,  # обязательное поле
                        "currencyId": "RUR",  # обязательное поле
                        "param": {
                            "@name": helpers.code_unicode("Скидка"),  # не обязательное поле
                            "#text": str,  # не обязательное поле
                        },
                    },
                    extra=PREVENT_EXTRA,
                )

                check.equal(S(offer_schema) == random_offer, True, "Offer schema mismatch")
