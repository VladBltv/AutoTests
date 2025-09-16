import allure
from allure_commons.types import Severity
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.catalog.private import CatalogPrivate


class TestRemoveInventories(QueriesCatalog, CatalogPrivate):
    @allure.id("2578")
    @allure.title("Очищение остатков при удалении/скрытии товара")
    @allure.description("Проверяем, что при скрытии/удалении товара по нему очищаются все остатки")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    @allure.label("feature", "Обновление остатков")
    def test_remove_with_delete_product(self):
        with allure.step("Находим товар, который есть в наличии в фф и омни2"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni=None)
            product = self.query_by_conditions(table="variations", conditions=[f"id = {variation[0]['variation_id']}"])
            product_id = product[0]["product_id"]

        with allure.step("Скрываем/удаляем товар через апи"):
            delete_response = self.api_products.delete_product(product_id=product_id)
            assert delete_response.status_code == 200

        with allure.step("Проверяем, что по товару больше нет остатков в таблице product_inventories по всем складам"):
            count = self.count_in_product_inventories_by_key(key="product_id", value=product_id)
            assert count == 0

        with allure.step("Проверяем, что в товаре и вариантах товара обнулилось поле fulfilment_qty"):
            product = self.query_by_conditions(table="variations", conditions=[f"id = {variation[0]['variation_id']}"])
            assert product[0]["fulfilment_qty"] == 0

            variations = self.query_by_conditions(table="variations", conditions=[f"product_id = {product_id}"])
            assert all(item["fulfilment_qty"] == 0 for item in variations)

        with allure.step("Находим товар, который есть в наличии в сфс и омни1"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None, qty_omni="> 1")
            product = self.query_by_conditions(table="variations", conditions=[f"id = {variation[0]['variation_id']}"])
            product_id = product[0]["product_id"]

        with allure.step("Скрываем/удаляем товар через апи"):
            delete_response = self.api_products.delete_product(product_id=product_id)
            assert delete_response.status_code == 200

        with allure.step("Проверяем, что по товару больше нет остатков в таблице product_inventories по всем складам"):
            count = self.count_in_product_inventories_by_key(key="product_id", value=product_id)
            assert count == 0

        with allure.step("Проверяем, что в товаре и вариантах товара обнулилось поле sfs_qty"):
            product = self.query_by_conditions(table="variations", conditions=[f"id = {variation[0]['variation_id']}"])
            assert product[0]["sfs_qty"] == 0

            variations = self.query_by_conditions(table="variations", conditions=[f"product_id = {product_id}"])
            assert all(item["sfs_qty"] == 0 for item in variations)

    @allure.id("2577")
    @allure.title("Очищение остатков при удалении/скрытии варианта товара")
    @allure.description("Проверяем, что при скрытии/удалении варианта по нему очищаются все остатки")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    @allure.label("feature", "Обновление остатков")
    def test_remove_with_delete_variation(self):
        with allure.step("Находим товар, который есть в наличии в фф и омни2"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni=None)
            product = self.query_by_conditions(table="variations", conditions=[f"id = {variation[0]['variation_id']}"])
            product_id = product[0]["product_id"]
            variation_id = product[0]["id"]

        with allure.step("Скрываем/удаляем вариант через апи"):
            delete_response = self.api_products.delete_variation(product_id=product_id, variation_id=variation_id)
            assert delete_response.status_code == 200

        with allure.step(
            "Проверяем, что по варианту больше нет остатков в таблице  product_inventories по всем складам"
        ):
            count = self.count_in_product_inventories_by_key(key="variation_id", value=variation_id)
            assert count == 0

        with allure.step("Проверяем, что в варианте товара обнулилось поле fulfilment_qty"):
            variation_db = self.query_by_conditions(table="variations", conditions=[f"id = {variation_id}"])
            assert variation_db[0]["fulfilment_qty"] == 0

        with allure.step("Проверяем, что в товаре пересчиталось поле fulfilment_qty с учетом удаленного варианта"):
            product_db = self.query_by_conditions(table="products", conditions=[f"id = {product_id}"])[0]
            conditions = [f"product_id = {product_id} and store_id = 1"]
            sum_qty = self.sum_in_product_inventories_by_keys(sum_colummn="qty", conditions=conditions)
            assert product_db["fulfilment_qty"] == sum_qty

        with allure.step("Находим товар, который есть в наличии в сфс и омни1"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None, qty_omni="> 1")
            product = self.query_by_conditions(table="variations", conditions=[f"id = {variation[0]['variation_id']}"])
            product_id = product[0]["product_id"]
            variation_id = product[0]["id"]

        with allure.step("Скрываем/удаляем вариант через апи"):
            delete_response = self.api_products.delete_variation(product_id=product_id, variation_id=variation_id)
            assert delete_response.status_code == 200

        with allure.step(
            "Проверяем, что по варианту больше нет остатков в таблице  product_inventories по всем складам"
        ):
            count = self.count_in_product_inventories_by_key(key="variation_id", value=variation_id)
            assert count == 0

        with allure.step("Проверяем, что в варианте товара обнулилось поле sfs_qty"):
            variation_db = self.query_by_conditions(table="variations", conditions=[f"id = {variation_id}"])
            assert variation_db[0]["sfs_qty"] == 0

        with allure.step("Проверяем, что в товаре пересчиталось поле sfs_qty с учетом удаленного варианта"):
            product_db = self.query_by_conditions(table="products", conditions=[f"id = {product_id}"])[0]
            conditions = [f"product_id = {product_id} and store_id = 500"]
            sum_qty = self.sum_in_product_inventories_by_keys(sum_colummn="qty", conditions=conditions)
            assert product_db["sfs_qty"] == sum_qty

    @allure.id("2579")
    @allure.title("Очищение остатков при удалении/скрытии магазина омни1")
    @allure.description("Проверяем, что при скрытии/удалении магазина омни1 по нему очищаются все остатки")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    @allure.label("feature", "Обновление остатков")
    def test_remove_with_delete_store(self):
        with allure.step("Находим магазин, у которого есть остатки"):
            variation_id, product_id, store_id, city_id = self.find_in_product_inventories(qty=4)
            store_id, store_external_id = self.store_by_city(city_id=city_id)

        with allure.step("Скрываем/удаляем магазин через апи"):
            store_response = self.api_stores.update_store(
                store_id=store_id, city_id=city_id, external_id=store_external_id, is_active=False
            )
            assert store_response.status_code == 200

        with allure.step("Проверяем, что по магазину больше нет остатков"):
            count = self.count_in_product_inventories_by_key(key="store_id", value=store_id)
            assert count == 0

    @allure.id("2580")
    @allure.title("Очищение остатков при размораживании товара")
    @allure.description("Проверяем, что при размораживании товара по нему очищаются все остатки")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Product")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Catalog")
    @allure.label("feature", "Обновление остатков")
    def test_remove_with_frozen(self):
        with allure.step("Находим товар в наличии в омни1 и фф"):
            variation_id = self.find_omniAndSf_stocks(city_id=2, store_id=1, qty=3)
            product = self.get_product_by_variation(variation_id=variation_id)
            article = product["article"]
            product_id = product["id"]

        with allure.step("Замораживаем и размораживаем товар в омни1"):
            frozen_response = self.api_frozen.update(frozen_type=["omni"], article=article)
            assert frozen_response.status_code == 200

            frozen_response = self.api_frozen.update(frozen_type=["omni"], article=article, is_delete="1")
            assert frozen_response.status_code == 200

        with allure.step("Проверяем, что по товару больше нет остатков по омни1 магазинам, а в фф есть"):
            conditions = ["city_id", "is not", "null", "and", "product_id", "=", f"{product_id}"]
            count_omni = self.count_in_product_inventories_by_keys(conditions=conditions)
            assert count_omni == 0

            conditions = ["city_id", "is ", "null", "and", "product_id", "=", f"{product_id}"]
            count_ff = self.count_in_product_inventories_by_keys(conditions=conditions)
            assert count_ff > 0

        with allure.step("Находим товар в наличии в омни1 и фф"):
            variation_id = self.find_omniAndSf_stocks(city_id=2, store_id=1, qty=4)
            product = self.get_product_by_variation(variation_id=variation_id)
            article = product["article"]
            product_id = product["id"]

        with allure.step("Замораживаем и размораживаем товар в фф и омни2"):
            frozen_response = self.api_frozen.update(frozen_type=["fulfilment"], article=article)
            assert frozen_response.status_code == 200

            frozen_response = self.api_frozen.update(frozen_type=["fulfilment"], article=article, is_delete="1")
            assert frozen_response.status_code == 200

            frozen_response = self.api_frozen.update(frozen_type=["omni2"], article=article)
            assert frozen_response.status_code == 200

            frozen_response = self.api_frozen.update(frozen_type=["omni2"], article=article, is_delete="1")
            assert frozen_response.status_code == 200

        with allure.step("Проверяем, что по товару больше нет остатков по фф и омни2, а в омни есть"):
            conditions = ["store_id", "in", "(1,2)", "and", "product_id", "=", f"{product_id}"]
            count_ff = self.count_in_product_inventories_by_keys(conditions=conditions)
            assert count_ff == 0

            conditions = ["city_id", "is not", "null", "and", "product_id", "=", f"{product_id}"]
            count_omni = self.count_in_product_inventories_by_keys(conditions=conditions)
            assert count_omni > 0
