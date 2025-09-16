import allure
from allure_commons.types import Severity
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from pytest_check import check
from utils.database import filling_out_table
import os


class TestPrepareDataForAnyqueryFeeds(QueriesCatalog):
    @allure.title("Подготовка данных для фидов anyquery")
    @allure.severity(Severity.CRITICAL)
    @allure.tag("critical")
    @allure.label("service", "Catalog")
    @allure.feature("Anyquery", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("""Готовим данные   для фида anyquery""")
    def test_prepare_data_for_anyquery_feeds(self):
        with allure.step("Трешхолд по количеству"):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            min_qty_omni = os.getenv("MIN_QTY_OMNI")

        with allure.step("Подготовака товара, который заморожен только по ff и есть в наличии только в ff"):
            with allure.step("Найти товар, который заморожен только по ff и есть в наличии только в ff"):
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=None, ff_frozen=True
                )

            with allure.step("Если товара нет, то изменить данные в базе"):
                if len(offers_base) == 0:
                    offers_base = self.find_variation_by_availability_condition(qty_ff=f">= {min_qty_ff}", qty_omni=None)
                    variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                    product_id = variation_data["product_id"]
                    data = {
                        "table": "products",
                        "field_name": ["fulfilment_frozen"],
                        "record_identifier": "id",
                        "data": [(True, product_id)],
                    }
                    filling_out_table(data=data, service="catalog")

            with allure.step("Проверить, что товар появился в базе"):
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=f">= {min_qty_ff}", qty_omni=None, ff_frozen=True
                )
                check.equal(len(offers_base), 1, "Товар должен быть в базе")

        with allure.step("Подготовака товара, который заморожен только по онми и есть в наличии только в онми"):
            offers_base = self.find_variation_by_availability_condition(qty_ff=None, qty_omni=f">= {min_qty_omni}", omni_frozen=True, city_id_in=2)

            with allure.step("Если товара нет, то изменить данные в базе"):
                if len(offers_base) == 0:
                    offers_base = self.find_variation_by_availability_condition(qty_ff=None, qty_omni=f">= {min_qty_omni}", city_id_in=2)
                    variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                    product_id = variation_data["product_id"]
                    data = {
                        "table": "products",
                        "field_name": ["omni_frozen"],
                        "record_identifier": "id",
                        "data": [(True, product_id)],
                    }
                    filling_out_table(data=data, service="catalog")

            with allure.step("Проверить, что товар появился в базе"):
                offers_base = self.find_variation_by_availability_condition(
                    qty_ff=None, qty_omni=f">= {min_qty_omni}", omni_frozen=True
                )
                check.equal(len(offers_base), 1, "Товар должен быть в базе")

        with allure.step("Подготовака товара, который заморожен по всем складам, но есть остаток по ff"):
            with allure.step("Найти в базе товар, который заморожен по всем складам, но есть остаток по ff"):
                offers_base = self.find_variation_by_availability_condition(
                    ff_frozen=True,
                    omni_frozen=True,
                    omni2_frozen=True,
                    sfs_frozen=True,
                    city_id_in=2,
                    qty_ff=f">= {min_qty_ff}",
                    qty_omni=f">= {min_qty_omni}",
                )

            with allure.step("Если товара нет, то изменить данные в базе"):
                if len(offers_base) == 0:
                    offers_base = self.find_variation_by_availability_condition(
                        qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", city_id_in=2
                    )
                    variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                    product_id = variation_data["product_id"]
                    data = {
                        "table": "products",
                        "field_name": [
                            "fulfilment_frozen",
                            "omni_frozen",
                            "omni2_frozen",
                            "sfs_frozen",
                        ],
                        "record_identifier": "id",
                        "data": [
                            (True, True, True, True, product_id),
                        ],
                    }
                    filling_out_table(data=data, service="catalog")

            with allure.step("Проверить, что товар появился в базе"):
                offers_base = self.find_variation_by_availability_condition(
                    ff_frozen=True,
                    omni_frozen=True,
                    omni2_frozen=True,
                    sfs_frozen=True,
                    city_id_in=2,
                    qty_ff=f">= {min_qty_ff}",
                    qty_omni=f">= {min_qty_omni}",
                )
                check.equal(len(offers_base), 1, "Товар должен быть в базе")

        with allure.step(
            "Подготовака товара, который заморожен по ff и есть остаток по ff но активен в омни и есть наличие в омни"
        ):
            with allure.step(
                "Найти в базе товар, который заморожен по ff и есть остаток по ff но активен в омни и есть наличие в омни"
            ):
                offers_base = self.find_variation_by_availability_condition(
                    ff_frozen=True, qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", city_id_in=2
                )

            with allure.step("Если товара нет, то изменить данные в базе"):
                if len(offers_base) == 0:
                    offers_base = self.find_variation_by_availability_condition(
                        qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", city_id_in=2
                    )
                    variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                    product_id = variation_data["product_id"]

                    data = {
                        "table": "products",
                        "field_name": ["fulfilment_frozen"],
                        "record_identifier": "id",
                        "data": [(True, product_id)],
                    }
                    filling_out_table(data=data, service="catalog")

            with allure.step("Проверить, что товар появился в базе"):
                offers_base = self.find_variation_by_availability_condition(
                    ff_frozen=True, qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", city_id_in=2
                )
                check.equal(len(offers_base), 1, "Товар должен быть в базе")

        with allure.step(
            "Подготовака товара, который заморожен по омни есть остаток по омни, но активен по ff и есть наличие по ff"
        ):
            with allure.step(
                "Найти в базе товар, который заморожен по омни есть остаток по омни, но активен по ff и есть наличие по ff"
            ):
                offers_base = self.find_variation_by_availability_condition(
                    omni_frozen=True, qty_omni=f">= {min_qty_omni}", qty_ff=f">= {min_qty_ff}", city_id_in=2
                )

            with allure.step("Если товара нет, то изменить данные в базе"):
                if len(offers_base) == 0:
                    offers_base = self.find_variation_by_availability_condition(
                        qty_ff=f">= {min_qty_ff}", qty_omni=f">= {min_qty_omni}", city_id_in=2
                    )
                    variation_data = self.entity_by_id(table="variations", id=offers_base[0]["variation_id"])
                    product_id = variation_data["product_id"]

                    data = {
                        "table": "products",
                        "field_name": ["omni_frozen"],
                        "record_identifier": "id",
                        "data": [(True, product_id)],
                    }
                    filling_out_table(data=data, service="catalog")

            with allure.step("Проверить, что товар появился в базе"):
                offers_base = self.find_variation_by_availability_condition(
                    omni_frozen=True, qty_omni=f">= {min_qty_omni}", qty_ff=f">= {min_qty_ff}", city_id_in=2
                )
                check.equal(len(offers_base), 1, "Товар должен быть в базе")

        with allure.step(
            "Подготовака товара, который есть в наличии только по нужному городу, но у магазина pickup_enabled_omni1 = false"
        ):
            with allure.step(
                "Найти в базе товар, который есть в наличии только по нужному городу, но у магазина pickup_enabled_omni1 = false"
            ):
                offers_base = self.find_variation_by_availability_condition(
                    city_id_in=2, qty_ff=None, qty_omni=f">= {min_qty_omni}", pickup_enabled_omni1=False
                )

            with allure.step("Если товара нет, то изменить данные в базе"):
                if len(offers_base) == 0:
                    stores = self.get_omni_stores_with_stock(offers_base[0]["variation_id"], 2)

                    for store in stores:
                        store_id = store["store_id"]
                        data = {
                            "table": "stores",
                            "field_name": ["pickup_enabled_omni1"],
                            "record_identifier": "id",
                            "data": [(False, store_id)],
                        }
                        filling_out_table(data=data, service="catalog")

            with allure.step("Проверить, что товар появился в базе"):
                offers_base = self.find_variation_by_availability_condition(
                    city_id_in=2, qty_ff=None, qty_omni=f">= {min_qty_omni}", pickup_enabled_omni1=False
                )
                check.equal(len(offers_base), 1, "Товар должен быть в базе")
