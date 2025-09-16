import allure

from allure_commons.types import Severity
from befree.api_model.catalog.public import CatalogPublic
from befree.api_model.catalog.private import CatalogPrivate
from befree.api_model.config.public import ConfigPublic
from befree.api_model.config.private import ConfigPrivate
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.config.db_queries.queries import QueriesConfig
from befree.api_model.test_data.product_card import payments
from utils.helpers import Helpers


class TestConfig(CatalogPublic, CatalogPrivate, ConfigPublic, ConfigPrivate, QueriesConfig, QueriesCatalog):

    # Для запуска тестов необходимо выключить кеш в каталоге CACHE_PAYMENTS_ENABLED=false
    @allure.id("2544")
    @allure.title("Методы оплат на странице товара с выключенным омни2")
    @allure.label("Service", "Config")
    @allure.label("Service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Product")
    @allure.description("Проверяем методы оплат в зависимости от настроек в конфигах и доступности варианта в городе, где выключен омни2")
    def test_product_payments_omni2_off(self):
        fias_id = "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"
        golden_record = "mosk-941139"

        with allure.step("Находим товар, который есть в наличии в фф и омни"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=6, store_id=1)
            product = self.get_product_by_variation(variation_id=variation)

            with allure.step("Включаем все методы оплаты для всех методов доставок"):
                payment_settings = self.api_private_config.update(configs=payments.all_on)
                assert payment_settings.status_code == 204

            with allure.step("Отправляем запрос на получение товара"):
                product_response = self.api_product.get(article=product["article"], fias_id=fias_id, golden_record=golden_record)
                assert product_response.status_code == 200

            with allure.step("Проверяем, что для варианта доступны все методы оплаты"):
                variations_response = product_response.json()["data"]["variations"]
                index = Helpers().index_value_key_in_list(iterable=variations_response, key="id", value=variation)

                assert "cash" in variations_response[index]["payments"]
                assert "sber" in variations_response[index]["payments"]
                assert "podeli" in variations_response[index]["payments"]
                assert "sbp" in variations_response[index]["payments"]

        with allure.step("Находим товар, который есть в наличии только в фф"):
            stock = self.find_stocks_only_ff(qty=3)
            variation = stock["variation_id"]
            product = self.get_product_by_variation(variation_id=variation)

            with allure.step("Включаем для курьера и пвз только сбер и сбп"):
                payment_settings = self.api_private_config.update(configs=payments.ff_sber_sbp_on)
                assert payment_settings.status_code == 204

            with allure.step("Отправляем запрос на получение товара"):
                product_response = self.api_product.get(article=product["article"], fias_id=fias_id, golden_record=golden_record)
                assert product_response.status_code == 200

            with allure.step("Проверяем, что для варианта доступен только подели"):
                variations_response = product_response.json()["data"]["variations"]
                index = Helpers().index_value_key_in_list(iterable=variations_response, key="id", value=variation)

                assert "podeli" not in variations_response[index]["payments"]
                assert "cash" not in variations_response[index]["payments"]
                assert "sber" in variations_response[index]["payments"]
                assert "sbp" in variations_response[index]["payments"]

        with allure.step("Находим товар, который есть в наличии только в омни"):
            stock = self.find_stocks_only_omni(value_omni2=False, qty=3)
            variation = stock["variation_id"]
            product = self.get_product_by_variation(variation_id=variation)
            fias_id, golden_record = self.get_city_by_store(store_id=stock["store_id"])

            with allure.step("Включаем для омни1 только подели"):
                payment_settings = self.api_private_config.update(configs=payments.omni1_only_podeli_on)
                assert payment_settings.status_code == 204

            with allure.step("Отправляем запрос на получение товара"):
                product_response = self.api_product.get(article=product["article"], fias_id=fias_id, golden_record=golden_record)
                assert product_response.status_code == 200

            with allure.step("Проверяем, что для варианта доступен только подели"):
                variations_response = product_response.json()["data"]["variations"]
                index = Helpers().index_value_key_in_list(iterable=variations_response, key="id", value=variation)

                assert "podeli" in variations_response[index]["payments"]
                assert "cash" not in variations_response[index]["payments"]
                assert "payture" not in variations_response[index]["payments"]
                assert "sbp" not in variations_response[index]["payments"]

        with allure.step("Включаем все методы оплаты для всех методов доставок"):
            payment_settings = self.api_private_config.update(configs=payments.all_on)
            assert payment_settings.status_code == 204

    @allure.id("2545")
    @allure.title("Методы оплат на странице товара с включенным омни2")
    @allure.label("Service", "Config")
    @allure.label("Service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Product")
    @allure.description(
        "Проверяем методы оплат в зависимости от настроек в конфигах и доступности варианта в городе, где включен омни2"
    )
    def test_product_payments_omni2_on(self):
        with allure.step("Находим товар, который есть в наличии только в фф и омни2"):
            stock = self.find_stocks_only_ff(qty=3)
            variation = stock["variation_id"]
            product = self.get_product_by_variation(variation_id=variation)

            with allure.step("Ищем магазин и включаем у него омни2"):
                store_spb, store_external_id = self.store_by_city(city_id=2)
                response_omni2_on = self.api_stores.update_store(
                    store_id=store_spb,
                    city_id=2,
                    pickup_enabled_omni2=1,
                    external_id=store_external_id,
                )
                assert response_omni2_on.status_code == 200

                fias_id, golden_record = self.get_city_by_store(store_id=store_spb)

            with allure.step("Включаем для каждого типа доставки свой тип оплаты: омни1 только Сбер, омни2 только Подели, курьер только СБП, ПВЗ только При получении"):
                payment_settings = self.api_private_config.update(configs=payments.one_to_one)
                assert payment_settings.status_code == 204

            with allure.step("Отправляем запрос на получение товара"):
                product_response = self.api_product.get(
                    article=product["article"], fias_id=fias_id, golden_record=golden_record
                )
                assert product_response.status_code == 200

            with allure.step("Проверяем, что для варианта доступны все оплаты"):
                variations_response = product_response.json()["data"]["variations"]
                index = Helpers().index_value_key_in_list(iterable=variations_response, key="id", value=variation)

                assert "podeli" in variations_response[index]["payments"]
                assert "cash" in variations_response[index]["payments"]
                assert "sbp" in variations_response[index]["payments"]
                assert "sber" not in variations_response[index]["payments"]

        with allure.step("Находим товар, который есть в наличии только в омни"):
            stock = self.find_variation_by_availability_condition(qty_omni="> 1", city_id_in=2, qty_ff=None)
            variation = stock[0]["variation_id"]
            product = self.get_product_by_variation(variation_id=variation)

            with allure.step("Включаем для каждого типа доставки свой тип оплаты"):
                payment_settings = self.api_private_config.update(configs=payments.one_to_one)
                assert payment_settings.status_code == 204

            with allure.step("Отправляем запрос на получение товара"):
                product_response = self.api_product.get(article=product["article"])
                assert product_response.status_code == 200

            with allure.step("Проверяем, что для варианта доступен только сбер"):
                variations_response = product_response.json()["data"]["variations"]
                index = Helpers().index_value_key_in_list(iterable=variations_response, key="id", value=variation)

                assert "podeli" not in variations_response[index]["payments"]
                assert "cash" not in variations_response[index]["payments"]
                assert "sber" in variations_response[index]["payments"]
                assert "sbp" not in variations_response[index]["payments"]

        with allure.step("Включаем все методы оплаты для всех методов доставок"):
            payment_settings = self.api_private_config.update(configs=payments.all_on)
            assert payment_settings.status_code == 204
