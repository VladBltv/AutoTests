import time
import allure

from befree.api_model.orders.public import OrdersPublic
from befree.api_model.orders.db_queries.queries import QueriesOrders
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from mimesis import Person
from allure_commons.types import Severity
from befree.api_model.customer import Customer


class TestMergingCarts(OrdersPublic, QueriesOrders, QueriesCatalog):
    @allure.id("2532")
    @allure.title("Мерж корзины: I >> II")
    @allure.description(
        "Проверить, что при мерже корзины, если в первой корзине на вкладках delivery и omni количество одного и того же больше чем во второй корзине, то при мерже будет количество из первой корзины"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts1(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(qty=5)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart1 = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Создаем вторую корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 1}]
            cart2 = self.api_cart.create(items=items)
            assert cart2.status_code == 200

        with allure.step("Логируемся под этим же пользователем"):
            login_customer = Customer(email=email, password=password).login()
            time.sleep(5)

            assert login_customer.status_code == 200
            customer_auth_token_new = login_customer.json()["token"]

        with allure.step("Апдейтим вторую корзину  -> корзины мержатся"):
            cart2 = self.api_cart.get(cart_uuid=cart2.json()["data"]["cartUuid"], token=customer_auth_token_new)
            assert cart2.status_code == 200

        with allure.step(
                "Проверяем в БД, что после мержа во второй корзине количество совпадает с количеством в первой корзине"):
            ref_merge_cart = [{"id": variation_in_omni1, "qtyOmni": 5, "qtyDelivery": 5, 'ymList': None}]
            cart_items = self.get_cart_data(uuid=cart2.json()["data"]["cartUuid"])[0]["data"]["items"]
            assert cart_items == ref_merge_cart

    @allure.id("2533")
    @allure.title("Мерж корзины: I << II")
    @allure.description(
        "Проверить, что при мерже корзины, если в первой корзине на вкладках delivery и omni количество одного и того же меньше чем во второй корзине, то при мерже будет количество из второй корзины"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts2(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 2}]
            cart1 = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Создаем вторую корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart2 = self.api_cart.create(items=items)
            assert cart2.status_code == 200

        with allure.step("Логируемся под этим же пользователем"):
            login_customer = Customer(email=email, password=password).login()
            time.sleep(5)

            assert login_customer.status_code == 200
            customer_auth_token = login_customer.json()["token"]

        with allure.step("Апдейтим вторую корзину  -> корзины мержатся"):
            cart2 = self.api_cart.get(cart_uuid=cart2.json()["data"]["cartUuid"], token=customer_auth_token)
            assert cart2.status_code == 200

        with allure.step(
                "Проверяем в БД, что после мержа во второй корзине количество совпадает с количеством во второй корзине"):
            ref_merge_cart = [{"id": variation_in_omni1, "qtyOmni": 5, "qtyDelivery": 5, 'ymList': None}]
            assert self.get_cart_data(cart2.json()["data"]["cartUuid"])[0]["data"]["items"] == ref_merge_cart

    @allure.id("2534")
    @allure.title("Мерж корзины: I <> II")
    @allure.description("Проверить, что при мерже корзины будет max количество товаров по вкладкам")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts3(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 1}]
            cart1 = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Апдейтим количество товаров в первой корзине"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart1_update = self.api_cart.update_qty(cart_uuid=cart1.json()["data"]["cartUuid"], current_tab="omni",
                                                    items=items)
            assert cart1_update.status_code == 200

        with allure.step("Создаем вторую корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart2 = self.api_cart.create(items=items)
            assert cart2.status_code == 200

        with allure.step("Апдейтим количество товаров в второй корзине"):
            items = [{"id": variation_in_omni1, "qty": 1}]
            cart2_update = self.api_cart.update_qty(cart_uuid=cart2.json()["data"]["cartUuid"], current_tab="omni",
                                                    items=items)
            assert cart2_update.status_code == 200

        with allure.step("Логируемся под этим же пользователем"):
            login_customer = Customer(email=email, password=password).login()
            time.sleep(10)

            assert login_customer.status_code == 200
            customer_auth_token = login_customer.json()["token"]

        with allure.step("Апдейтим вторую корзину  -> корзины мержатся"):
            cart2 = self.api_cart.get(cart_uuid=cart2.json()["data"]["cartUuid"], token=customer_auth_token)
            assert cart2.status_code == 200

        with allure.step("Проверяем в БД, что после мержа во второй корзине количество по омни и деливери = 5"):
            ref_merge_cart = [{"id": variation_in_omni1, "qtyOmni": 5, "qtyDelivery": 5, 'ymList': None}]
            assert self.get_cart_data(cart2.json()["data"]["cartUuid"])[0]["data"]["items"] == ref_merge_cart

    @allure.id("2528")
    @allure.title("Мерж корзины: I >< II")
    @allure.description("Проверить, что при мерже корзины будет max количество товаров по вкладкам")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts4(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart1 = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Апдейтим количество товаров в первой корзине"):
            items = [{"id": variation_in_omni1, "qty": 1}]
            cart1_update = self.api_cart.update_qty(cart_uuid=cart1.json()["data"]["cartUuid"], current_tab="omni",
                                                    items=items)
            assert cart1_update.status_code == 200

        with allure.step("Создаем вторую корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 1}]
            cart2 = self.api_cart.create(items=items)
            assert cart2.status_code == 200

        with allure.step("Апдейтим количество товаров в второй корзине"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart2_update = self.api_cart.update_qty(cart_uuid=cart2.json()["data"]["cartUuid"], current_tab="omni",
                                                    items=items)
            assert cart2_update.status_code == 200

        with allure.step("Логируемся под этим же пользователем"):
            login_customer = Customer(email=email, password=password).login()
            time.sleep(5)

            assert login_customer.status_code == 200
            customer_auth_token = login_customer.json()["token"]

        with allure.step("Апдейтим вторую корзину  -> корзины мержатся"):
            cart2 = self.api_cart.get(cart_uuid=cart2.json()["data"]["cartUuid"], token=customer_auth_token)
            assert cart2.status_code == 200

        with allure.step("Проверяем в БД, что после мержа во второй корзине количество по омни и деливери = 5"):
            ref_merge_cart = [{"id": variation_in_omni1, "qtyOmni": 5, "qtyDelivery": 5, 'ymList': None}]
            assert self.get_cart_data(cart2.json()["data"]["cartUuid"])[0]["data"]["items"] == ref_merge_cart

    @allure.id("2531")
    @allure.title("Мерж корзины: I == II + другие товары")
    @allure.description("Проверить, что при мерже корзины будет max количество товаров по вкладкам")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts5(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товары, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id1 = self.find_omni_stocks(10)
            variation_in_omni2, store_omni2, store_external_id2 = self.find_omni_stocks(20)

        with allure.step("Создаем первую корзину"):
            items = [
                {"id": variation_in_omni1, "qty": 1},
                {"id": variation_in_omni2, "qty": 1},
            ]
            cart1 = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Апдейтим количество товаров в первой корзине"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart1_update = self.api_cart.update_qty(
                cart_uuid=cart1.json()["data"]["cartUuid"], current_tab="omni", items=items)
            assert cart1_update.json()["data"]["cartUuid"]

        with allure.step("Создаем вторую корзину под неавторизованным пользователем"):
            items = [
                {"id": variation_in_omni1, "qty": 1},
            ]
            cart2 = self.api_cart.create(items=items)
            assert cart2.json()["data"]["cartUuid"]

        with allure.step("Апдейтим количество товаров в второй корзине"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart2_update = self.api_cart.update_qty(cart_uuid=cart2.json()["data"]["cartUuid"], current_tab="omni",
                                                    items=items)
            assert cart2_update.json()["data"]["cartUuid"]

        with allure.step("Логируемся под этим же пользователем"):
            login_customer = Customer(email=email, password=password).login()
            time.sleep(10)

            assert login_customer.status_code == 200
            customer_auth_token = login_customer.json()["token"]

        with allure.step("Апдейтим вторую корзину  -> корзины мержатся"):
            cart2 = self.api_cart.get(cart_uuid=cart2.json()["data"]["cartUuid"], token=customer_auth_token)
            assert cart2.status_code == 200

        with allure.step("Проверяем в БД, что после мержа во второй корзине количество по омни и деливери = 5"):
            ref_merge_cart = [
                {"id": variation_in_omni1, "qtyOmni": 5, "qtyDelivery": 1, 'ymList': None},
                {"id": variation_in_omni2, "qtyOmni": 1, "qtyDelivery": 1, 'ymList': None},
            ]
            assert self.get_cart_data(cart2.json()["data"]["cartUuid"])[0]["data"]["items"] == ref_merge_cart

    @allure.id("2529")
    @allure.title("Мерж корзин: обычная + быстрая")
    @allure.description("Проверить, что обычная и быстрая корзина не мержатся")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts_fast1(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товары, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id1 = self.find_omni_stocks(5)
            variation_in_omni2, store_omni2, store_external_id2 = self.find_omni_stocks(2)

        with allure.step("Создаем обычную корзину под авторизованным пользователем"):
            items = [
                {"id": variation_in_omni1, "qty": 1},
            ]
            cart1 = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Создаем быструю корзину под этим же пользователем"):
            items = [
                {"id": variation_in_omni2, "qty": 2},
            ]
            fast_cart = self.api_cart.create_fast_cart(items=items, token=customer_auth_token)
            assert fast_cart.status_code == 200

        with allure.step("Проверяем, что корзины не смержились"):
            with allure.step("Сверяем данные обычной корзины"):
                cart1_data = self.get_cart_data(cart1.json()["data"]["cartUuid"])
                assert (cart1_data[0]["data"]["items"][0]["id"] == variation_in_omni1
                        and cart1_data[0]["data"]["items"][0]["qtyOmni"] == 1)

            with allure.step("Сверяем данные быстрой корзины"):
                fast_cart_data = self.get_cart_data(fast_cart.json()["data"]["cartUuid"])
                assert (
                        fast_cart_data[0]["data"]["items"][0]["id"] == variation_in_omni2
                        and fast_cart_data[0]["data"]["items"][0]["qtyOmni"] == 1
                        and len(fast_cart_data[0]["data"]["items"]) == len(cart1_data[0]["data"]["items"]) == 1
                )

    @allure.id("2530")
    @allure.title("Мерж корзин: быстрая + обычная")
    @allure.description("Проверить, что обычная и быстрая корзина не мержатся")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Мерж корзины")
    def test_merge_carts_fast2(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            register_customer = Customer(email=email, password=password).register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товары, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id1 = self.find_omni_stocks(2)
            variation_in_omni2, store_omni2, store_external_id2 = self.find_omni_stocks(5)

        with allure.step("Создаем быструю корзину под авторизованным пользователем"):
            items = [
                {"id": variation_in_omni1, "qty": 2},
            ]
            fast_cart = self.api_cart.create_fast_cart(items=items, token=customer_auth_token)
            assert fast_cart.status_code == 200

        with allure.step("Создаем обычную корзину под этим же пользователем"):
            items_1 = [
                {"id": variation_in_omni2, "qty": 1},
            ]
            cart1 = self.api_cart.create(items=items_1, token=customer_auth_token)
            assert cart1.status_code == 200

        with allure.step("Проверяем, что корзины не смержились"):
            with allure.step("Сверяем данные обычной корзины"):
                cart1_data = self.get_cart_data(cart1.json()["data"]["cartUuid"])
                assert cart1_data[0]["data"]["items"][0]["id"] == variation_in_omni2 and \
                       cart1_data[0]["data"]["items"][0]["qtyOmni"] == 1
            with allure.step("Сверяем данные быстрой корзины"):
                fast_cart_data = self.get_cart_data(fast_cart.json()["data"]["cartUuid"])
                assert (
                        fast_cart_data[0]["data"]["items"][0]["id"] == variation_in_omni1
                        and fast_cart_data[0]["data"]["items"][0]["qtyOmni"] == 1
                        and len(fast_cart_data[0]["data"]["items"]) == len(cart1_data[0]["data"]["items"]) == 1
                )
