import time
import allure
import os
import requests

from befree.api_model.orders.public import OrdersPublic
from befree.api_model.config.private import ConfigPrivate
from befree.api_model.orders.public.payment_available.shemas import payment_available
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders import utils
from pytest_voluptuous import S
from befree.api_model.customer import Customer
from befree.api_model.test_data.order import (
    payment_cash,
    payment_common,
    payment_podeli,
    payment_sbp,
    payment_sber,
)
from dotenv import load_dotenv
from mimesis import Person
from allure_commons.types import Severity
from pytest_check import check


class TestPayments(OrdersPublic, QueriesCatalog, ConfigPrivate):
    @allure.id("2691")
    @allure.title("Оформление заказа с оплатой sber, омни 1, быстрая корзина")
    @allure.description(
        "Проверяем, что при отправке запроса на оформление заказа с sber в ответе приходят данные для этого метода оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Sber")
    def test_payment_sber(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)
            fias_id, golden_record = self.get_city_by_store(store_omni1)

        with allure.step("Создаем быструю корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create_fast_cart(
                items=items, token=customer_auth_token, fias_id=fias_id, golden_record=golden_record
            )
            assert cart.status_code == 200
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с доставкой в магазин омни1"):
            cart_with_shipping = self.api_cart.update_reserveinstore(
                cart_uuid=cart_uuid,
                store_id=store_omni1,
                store_external_id=store_external_id,
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Устанавливаем кастомера в корзине"):
            customer = customer_init.get_customer(token=customer_auth_token)
            assert customer.status_code == 200

            cart_with_customer = self.api_cart.set_customer(
                cart_uuid=cart_uuid,
                customer=customer.json(),
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_customer.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с методом оплаты sber"):
            cart_with_payment = self.api_cart.update_payment(
                cart_uuid=cart_uuid, method="sber", fias_id=fias_id, golden_record=golden_record
            )
            assert cart_with_payment.json()["data"]["cartUuid"]

        with allure.step("Оформляем заказ"):
            order = self.api_order.send_order(
                cart_uuid=cart_with_payment.json()["data"]["cartUuid"],
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert order.status_code == 200

        with (allure.step("Проверяем, что пришли корректные данные для метода оплаты sber")):
            redirectUrl = order.json()["data"]["redirectUrl"]
            assert order.json()["data"]["paymentMethods"] == "sber"
            assert "https://sbox.payecom.ru/pay_ru?orderId=" in redirectUrl

    @allure.id("2460")
    @allure.title("Оформление заказа с оплатой sbp, омни 1, обычная корзина")
    @allure.description(
        "Проверяем, что при отправке запроса на оформление заказа с sbp в ответе приходят данные для этого метода оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "SBP")
    def test_payment_sbp(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)
            fias_id, golden_record = self.get_city_by_store(store_omni1)

        with allure.step("Создаем обычную корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create(
                items=items, token=customer_auth_token, fias_id=fias_id, golden_record=golden_record
            )
            assert cart.status_code == 200

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с current_tab = omni"):
            cart_change_tab = self.api_cart.update_current_tab(cart_uuid=cart_uuid, fias_id=fias_id,
                golden_record=golden_record, current_tab="omni")

            assert cart_change_tab.status_code == 200

        with allure.step("Обновляем корзину с доставкой в магазин омни1"):
            cart_with_shipping = self.api_cart.update_reserveinstore(
                cart_uuid=cart_uuid,
                store_id=store_omni1,
                store_external_id=store_external_id,
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Устанавливаем кастомера в корзине"):
            customer = customer_init.get_customer(token=customer_auth_token)
            assert customer.status_code == 200

            cart_with_customer = self.api_cart.set_customer(
                cart_uuid=cart_uuid,
                customer=customer.json(),
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_customer.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с методом оплаты sbp"):
            cart_with_payment = self.api_cart.update_payment(
                cart_uuid=cart_uuid, method="sbp", fias_id=fias_id, golden_record=golden_record
            )
            assert cart_with_payment.json()["data"]["cartUuid"]

        with allure.step("Оформляем заказ"):
            order = self.api_order.send_order(
                cart_uuid=cart_with_payment.json()["data"]["cartUuid"],
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert order.status_code == 200

        with allure.step("Проверяем, что пришли корректные данные для метода оплаты sbp"):
            check_payload = requests.head(order.json()["data"]["metadata"]["payload"])
            assert (
                order.json()["data"]["paymentMethods"] == "sbp" and check_payload.status_code == 200
            )

    @allure.id("2459")
    @allure.title("Оформление заказа с оплатой cash, доставка ПВЗ, обычная корзина")
    @allure.description(
        "Проверяем, что при отправке запроса на оформление заказа с cash в ответе приходят данные для этого метода оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Cash")
    def test_payment_cash(self, goods):
        with allure.step("Создаем корзину под неавторизованным пользователем"):
            items = [{"id": goods["qty_2"]["id"], "qty": 1}]
            cart = self.api_cart.create(items=items)
            assert cart.status_code == 200

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickuppoints.status_code == 200

        with allure.step("Обновляем корзину с доставкой в ПВЗ"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Устанавливаем кастомера в корзине"):
            person = Person("en")
            customer = dict()
            customer["email"] = person.email()
            customer["first_name"] = person.first_name()
            customer["last_name"] = person.last_name()

            cart_with_customer = self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)
            assert cart_with_customer.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с методом оплаты cash"):
            cart_with_payment = self.api_cart.update_payment(cart_uuid=cart_uuid, method="cash")
            time.sleep(5)
            assert cart_with_payment.json()["data"]["cartUuid"]

        with allure.step("Оформляем заказ"):
            order = self.api_order.send_order(
                cart_uuid=cart_with_payment.json()["data"]["cartUuid"]
            )
            assert order.status_code == 200

        with allure.step("Проверяем, что пришли корректные данные для метода оплаты cash"):
            redirectUrl = order.json()["data"]
            # раскомментировать, когда сделают страницу успеха
            # check_url = requests.head(redirectUrl)
            load_dotenv()
            find_url = redirectUrl["redirectUrl"].find(os.getenv("SHOP_URL"))
            assert (
                order.json()["data"]["paymentMethods"] == "cash"
                # раскомментировать, когда сделают страницу успеха
                # and check_url.status_code == 200
                and find_url != -1
            )

    @allure.id("2461")
    @allure.title("Оформление заказа с оплатой podeli, омни1, быстрая корзина")
    @allure.description(
        "Проверяем, что при отправке запроса на оформление заказа с podeli в ответе приходят данные для этого метода оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Podeli")
    def test_payment_podeli(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)
            fias_id, golden_record = self.get_city_by_store(store_omni1)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create_fast_cart(
                items=items, token=customer_auth_token, fias_id=fias_id, golden_record=golden_record
            )
            assert cart.json()["data"]["cartUuid"]

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с доставкой в магазин омни1"):
            cart_with_shipping = self.api_cart.update_reserveinstore(
                cart_uuid=cart_uuid,
                store_id=store_omni1,
                store_external_id=store_external_id,
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Устанавливаем кастомера в корзине"):
            customer = customer_init.get_customer(token=customer_auth_token)
            assert customer.status_code == 200

            cart_with_customer = self.api_cart.set_customer(
                cart_uuid=cart_uuid,
                customer=customer.json(),
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_customer.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с методом оплаты podeli"):
            cart_with_payment = self.api_cart.update_payment(
                cart_uuid=cart_uuid, method="podeli", fias_id=fias_id, golden_record=golden_record
            )
            assert cart_with_payment.json()["data"]["cartUuid"]

        with allure.step("Оформляем заказ"):
            order = self.api_order.send_order(
                cart_uuid=cart_with_payment.json()["data"]["cartUuid"],
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert order.status_code == 200

        with allure.step("Проверяем, что пришли корректные данные для метода оплаты podeli"):
            assert order.json()["data"]["paymentMethods"] == "podeli"

    @allure.id("2464")
    @allure.title("Проверка получения методов оплат в зависимости от доставки. Для ОМНИ")
    @allure.description(
        "Проверяем, что, если метод оплаты при получении выключен для метода доставки ОМНИ, то он не приходит"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Cash")
    @allure.label("feature", "SBP")
    @allure.label("feature", "Podeli")
    @allure.label("feature", "Sber")
    def test_payment_methods_omni(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)
            fias_id, golden_record = self.get_city_by_store(store_omni1)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create_fast_cart(
                items=items, token=customer_auth_token, fias_id=fias_id, golden_record=golden_record
            )
            assert cart.status_code == 200

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Обновляем корзину с доставкой в магазин омни1"):
            cart_with_shipping = self.api_cart.update_reserveinstore(
                cart_uuid=cart_uuid,
                store_id=store_omni1,
                store_external_id=store_external_id,
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            assert payment_methods.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(payment_available) == payment_methods.json()

        with allure.step("Отключаем для омни1 все методы оплаты, кроме cash"):
            payment_settings = self.api_private_config.update(
                configs=payment_cash.query_for_omni1_off
            )
            assert payment_settings.status_code == 204

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            assert payment_methods.status_code == 200

        with allure.step("Проверяем, что пришел только cash"):
            assert (
                len(payment_methods.json()["data"]["paymentMethods"]) == 1
                and payment_methods.json()["data"]["paymentMethods"][0]["key"] == "cash"
            )

        with allure.step("Включаем все методы оплат для омни1"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2720")
    @allure.title("Проверка получения методов оплат в зависимости от доставки. Для SFS ПВЗ")
    @allure.description(
        "Проверяем, что, если метод оплаты Подели выключен для метода доставки SFS ПВЗ, то он не приходит в ответе доступных методов оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Cash")
    @allure.label("feature", "SBP")
    @allure.label("feature", "Podeli")
    @allure.label("feature", "Sber")
    def test_payment_methods_sfs_pickup(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            check.equal(register_customer.status_code, 200, "Status code should be 200")
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в sfs"):
            variation = self.find_variation_by_availability_condition(qty_sfs=">= 1", qty_ff=None)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(
                items=items, token=customer_auth_token, current_tab="delivery"
            )
            check.equal(cart.status_code, 200, "Status code should be 200")

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            check.equal(pickuppoints.status_code, 200, "Status code should be 200")

        with allure.step("Обновляем корзину с доставкой в ПВЗ"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            check.equal(
                cart_with_shipping.json()["data"]["cartUuid"],
                cart_uuid,
                "Cart uuid should be equal",
            )

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            check.equal(payment_methods.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            check.equal(
                S(payment_available) == payment_methods.json(),
                True,
                "Payment methods should be equal",
            )

        with allure.step("Отключаем для sfs доставки ПВЗ метод оплаты Podeli"):
            payment_settings = self.api_private_config.update(
                configs=payment_podeli.query_sfs_pickup_podeli_off
            )
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            check.equal(payment_methods.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что в ответе нет метода оплаты Podeli"):
            check.equal(
                "podeli"
                not in [
                    method["key"] for method in payment_methods.json()["data"]["paymentMethods"]
                ],
                True,
                "podeli method should not be present",
            )

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

    @allure.id("2719")
    @allure.title("Проверка получения методов оплат в зависимости от доставки. Для SFS Курьер")
    @allure.description(
        "Проверяем, что, если метод оплаты СБП выключен для метода доставки SFS Курьер, то он не приходит в ответе доступных методов оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Cash")
    @allure.label("feature", "SBP")
    @allure.label("feature", "Podeli")
    @allure.label("feature", "Sber")
    def test_payment_methods_sfs_delivery(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем   кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            check.equal(register_customer.status_code, 200, "Status code should be 200")
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в sfs"):
            variation = self.find_variation_by_availability_condition(qty_sfs=">= 1", qty_ff=None)

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(
                items=items, token=customer_auth_token, current_tab="delivery"
            )
            check.equal(cart.status_code, 200, "Status code should be 200")

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный интервал доставки"):
            address = utils.get_address()
            delivery_intervals = self.api_delivery.get_intervals(
                cart_uuid=cart_uuid, address=address["intervals"]
            )
            check.equal(delivery_intervals.status_code, 200, "Status code should be 200")
            interval_id = delivery_intervals.json()["data"]["services"][0]["dates"][0]["intervals"][
                0
            ]["id"]

        with (allure.step("Обновляем корзину с курьерской доставкой")):
            cart_with_shipping = self.api_cart.update_delivery(
                cart_uuid=cart_uuid, interval_id=interval_id, address=address["shipping"]
            )
            check.equal(
                cart_with_shipping.json()["data"]["cartUuid"],
                cart_uuid,
                "Cart uuid should be equal",
            )

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            check.equal(payment_methods.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            check.equal(
                S(payment_available) == payment_methods.json(),
                True,
                "Payment methods should be equal",
            )

        with allure.step("Отключаем для sfs доставки курьером метод оплаты СБП"):
            payment_settings = self.api_private_config.update(
                configs=payment_sbp.query_sfs_delivery_sbp_off
            )
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            check.equal(payment_methods.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что в ответе нет метода оплаты СБП"):
            check.equal(
                "sbp"
                not in [
                    method["key"] for method in payment_methods.json()["data"]["paymentMethods"]
                ],
                True,
                "sbp method should not be present",
            )

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

    @allure.id("2721")
    @allure.title("Проверка получения методов оплат в зависимости от доставки. Для SF Курьера")
    @allure.description(
        "Проверяем, что, если метод оплаты сбером выключен для метода доставки SF Курьер, то он не приходит в ответе доступных методов оплаты"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Cash")
    @allure.label("feature", "SBP")
    @allure.label("feature", "Podeli")
    @allure.label("feature", "Sber")
    def test_payment_methods_sf_delivery(self):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            check.equal(register_customer.status_code, 200, "Status code should be 200")
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Находим товар, который есть в наличии в sf"):
            variation = self.find_variation_by_availability_condition(qty_ff=">= 1")

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(
                items=items, token=customer_auth_token, current_tab="delivery"
            )
            check.equal(cart.status_code, 200, "Status code should be 200")

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный интервал доставки"):
            address = utils.get_address()
            delivery_intervals = self.api_delivery.get_intervals(
                cart_uuid=cart_uuid, address=address["intervals"]
            )
            check.equal(delivery_intervals.status_code, 200, "Status code should be 200")
            interval_id = delivery_intervals.json()["data"]["services"][0]["dates"][0]["intervals"][
                0
            ]["id"]

        with (allure.step("Обновляем корзину с курьерской доставкой")):
            cart_with_shipping = self.api_cart.update_delivery(
                cart_uuid=cart_uuid, interval_id=interval_id, address=address["shipping"]
            )
            check.equal(
                cart_with_shipping.json()["data"]["cartUuid"],
                cart_uuid,
                "Cart uuid should be equal",
            )

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            check.equal(payment_methods.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            check.equal(
                S(payment_available) == payment_methods.json(),
                True,
                "Payment methods should be equal",
            )

        with allure.step("Отключаем для доставки курьером метод оплаты сбером"):
            payment_settings = self.api_private_config.update(
                configs=payment_sber.query_sf_delivery_sber_off
            )
            check.equal(payment_settings.status_code, 204, "Status code should be 204")

        with allure.step("Получаем доступные методы оплат"):
            payment_methods = self.api_payment_available.get_payments_available(cart_uuid=cart_uuid)
            check.equal(payment_methods.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что в ответе нет метода оплаты Сбером"):
            check.equal(
                "sber"
                not in [
                    method["key"] for method in payment_methods.json()["data"]["paymentMethods"]
                ],
                True,
                "sber method should not be present",
            )

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            check.equal(payment_settings.status_code, 204, "Status code should be 204")
