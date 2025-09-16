import allure

from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.config.private import ConfigPrivate
from allure_commons.types import Severity
from pytest_check import check


class TestOutOfStock(OrdersPublic, QueriesCatalog, ConfigPrivate):
    @allure.id("2726")
    @allure.title("Товары не в наличии для быстрой корзины ")
    @allure.description(
        "В быстрой корзине для вкладки outOfStock анализируются остатки только по SFS и омни1. Если товар есть в "
        "наличии в SF или омни2, но его нет для SFS и омни1, то такой товар должен попасть в outOfStock для быстрой "
        "корзины"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_quick_cart_out_of_stock(self):
        with allure.step("Находим товар, которого нет в наличии нигде"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff=None, qty_omni=None)

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "Cart UUID should exist")

        with allure.step("Проверяем, что товар попал на вкладку outOfStock и не попал в omni и delivery"):
            tab = cart.json()["data"]["items"]
            assert len(tab["outOfStock"]) > 0
            check.greater(len(tab["outOfStock"]), 0, "Out of stock should be greater than 0")
            check.equal(tab["omni"], [], "Omni should be empty")
            check.equal(tab["delivery"], [], "Delivery should be empty")

        # with allure.step("Находим товар, который есть в наличии в фф и омни2"):
        #     variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni=None)
        #
        # with allure.step("Создаем быструю корзину с этим вариантом"):
        #     items = [{"id": variation[0]["variation_id"], "qty": 1}]
        #     cart = self.api_cart.create_fast_cart(items=items, current_tab="delivery")
        #     check.is_not_none(cart.json()["data"]["cartUuid"], "Cart UUID should exist")
        #
        # with allure.step("Проверяем, что товар попал на вкладку outOfStock и не попал в omni и delivery"):
        #     tab = cart.json()["data"]["items"]
        #     assert len(tab["outOfStock"]) > 0
        #     check.greater(len(tab["outOfStock"]), 0, "Out of stock should be greater than 0")
        #     check.equal(tab["omni"], [], "Omni should be empty")
        #     check.equal(tab["delivery"], [], "Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии в сфс"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None)

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке delivery"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "Out of stock should be None")
            # check.equal(tab["omni"], [], "Omni should be empty")
            check.greater(len(tab["delivery"]), 0, "Delivery should be greater than 0")

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation = self.find_variation_by_availability_condition(
                qty_omni="> 1", qty_sfs=None, qty_ff=None, city_id_in=2
            )

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="omni")
            check.is_not_none(cart.json()["data"]["cartUuid"], "Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке omni"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "Out of stock should be None")
            check.greater(len(tab["omni"]), 0, "Omni should be greater than 0")
            check.equal(tab["delivery"], [], "Delivery should be empty")

    @allure.id("2750")
    @allure.title("Товары не в наличии для обычной корзины ")
    @allure.description(
        "В обычной корзине для вкладки outOfStock анализируются остатки по SF, омни2 и омни1. Если товар есть в "
        "наличии в SFS, но его нет для SF и омни2 и омни1, то такой товар должен попасть в outOfStock обычной корзины"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_cart_out_of_stock(self):
        with allure.step("Находим товар, которого нет в наличии нигде"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff=None, qty_omni=None)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "1 Cart UUID should exist")

        with allure.step("Проверяем, что товар попал на вкладку outOfStock и не попал в omni и delivery"):
            tab = cart.json()["data"]["items"]
            check.greater(len(tab["outOfStock"]), 0, "2 Out of stock should be greater than 0")
            check.equal(tab["omni"], [], "3 Omni should be empty")
            check.equal(tab["delivery"], [], "4 Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии только в сфс"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None, qty_omni=None, city_id_in=2)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "5 Cart UUID should exist")

        with allure.step("Проверяем, что товар попал на вкладку outOfStock, и не попал в delivery и omni"):
            tab = cart.json()["data"]["items"]
            check.greater(len(tab["outOfStock"]), 0, "6 Out of stock should be greater than 0")
            check.equal(tab["omni"], [], "7 Omni should be empty")
            check.equal(tab["delivery"], [], "8 Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии в сфс и омни1"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None, qty_omni="> 1", city_id_in=2)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "9 Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock и delivery, но попал в omni"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "10 Out of stock should be None")
            check.greater(len(tab["omni"]), 0, "11 Omni should not be empty")
            check.equal(tab["delivery"], [], "12 Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии только в фф"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni=None)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "13 Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке delivery"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "14 Out of stock should be None")
            check.equal(tab["omni"], [], "15 Omni should be empty")
            check.greater(len(tab["delivery"]), 0, "16 Delivery should be greater than 0")

        with allure.step("Находим товар, который есть в наличии в фф и омни, но нет в sfs"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni="> 1", city_id_in=2)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            check.is_not_none(cart.json()["data"]["cartUuid"], "17 Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке delivery и omni"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "18 Out of stock should be None")
            check.greater(len(tab["omni"]), 0, "19 Delivery should be greater than 0")
            check.greater(len(tab["delivery"]), 0, "20 Delivery should be greater than 0")

    @allure.id("2750")
    @allure.title("Товары не в наличии для обычной корзины для города с омни2")
    @allure.description(
        "В обычной корзине для вкладки outOfStock анализируются остатки только по SF, омни2 и омни1. Если товар есть в "
        "наличии в SFS, но его нет для SF, омни2 и омни1, то такой товар должен попасть в outOfStock обычной корзины. "
        "Для города с включенным омни2 вкладка самовывоза формируется так же как для города без омни2"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_cart_out_of_stock_with_omni2(self):
        with allure.step("Опеределяем города с включенной опцией омни2"):
            conditions = ["omni_2 is true"]
            city_with_omni2 = self.query_by_conditions(table="cities", conditions=conditions)[0]
            fias_id = city_with_omni2["fias_id"]
            golden = city_with_omni2["golden_record"]
            city_id = city_with_omni2["id"]

        with allure.step("Находим товар, которого нет в наличии нигде"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff=None, qty_omni=None)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden)
            check.is_not_none(cart.json()["data"]["cartUuid"], "1 Cart UUID should exist")

        with allure.step("Проверяем, что товар попал на вкладку outOfStock и не попал в omni и delivery"):
            tab = cart.json()["data"]["items"]
            check.greater(len(tab["outOfStock"]), 0, "2 Out of stock should be greater than 0")
            check.equal(tab["omni"], [], "3 Omni should be empty")
            check.equal(tab["delivery"], [], "4 Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии только в сфс"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None, qty_omni=None,
                                                                      city_id_in=city_id)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden)
            check.is_not_none(cart.json()["data"]["cartUuid"], "5 Cart UUID should exist")

        with allure.step("Проверяем, что товар попал на вкладку outOfStock, и не попал в delivery и omni"):
            tab = cart.json()["data"]["items"]
            check.greater(len(tab["outOfStock"]), 0, "6 Out of stock should be greater than 0")
            check.equal(tab["omni"], [], "7 Omni should be empty")
            check.equal(tab["delivery"], [], "8 Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии в сфс и омни1"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None, qty_omni="> 1",
                                                                      city_id_in=city_id)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden)
            check.is_not_none(cart.json()["data"]["cartUuid"], "9 Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock и delivery, но попал в omni"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "10 Out of stock should be None")
            check.greater(len(tab["omni"]), 0, "11 Omni should not be empty")
            check.equal(tab["delivery"], [], "12 Delivery should be empty")

        with allure.step("Находим товар, который есть в наличии только в фф"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni=None)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden)
            check.is_not_none(cart.json()["data"]["cartUuid"], "13 Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке delivery"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "14 Out of stock should be None")
            check.equal(tab["omni"], [], "15 Omni should be empty")
            check.greater(len(tab["delivery"]), 0, "16 Delivery should be greater than 0")

        with allure.step("Находим товар, который есть в наличии в фф и омни, но нет в sfs"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni="> 1", city_id_in=city_id)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden)
            check.is_not_none(cart.json()["data"]["cartUuid"], "17 Cart UUID should exist")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке delivery и omni"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "18 Out of stock should be None")
            check.greater(len(tab["omni"]), 0, "19 Delivery should be greater than 0")
            check.greater(len(tab["delivery"]), 0, "20 Delivery should be greater than 0")
