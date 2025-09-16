import time
import allure

from mimesis import Person
from allure_commons.types import Severity
from befree.api_model.esb import EsbPublic
from befree.api_model.orders import utils
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.customer import Customer


class TestOrderSend(OrdersPublic, EsbPublic):
    @allure.id("2454")
    @allure.title("Оформление заказа омни1 в омс под авторизованным пользователем")
    @allure.description(
        "Проверяем, что заказ омни1 создается в омс под авторизованным пользователем"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление заказа")
    def test_order_authorized_user(self, goods):
        with allure.step("Формируем данные кастомера"):
            person = Person("en")
            email = person.email()
            password = "aA123456"

        with allure.step("Регистрируем кастомера и получаем токен"):
            customer_init = Customer(email=email, password=password)
            register_customer = customer_init.register()

            assert register_customer.status_code == 200
            customer_auth_token = register_customer.json()["token"]

        with allure.step("Создаем корзину под авторизованным пользователем"):
            items = [{"id": goods["qty_2"]["id"], "qty": 1}]
            cart = self.api_cart.create(items=items, token=customer_auth_token)
            assert cart.json()["data"]["cartUuid"] != None

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickuppoints.status_code == 200

        with allure.step("Обновляем корзину с доставкой в ПВЗ"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"] != None

        with allure.step("Устанавливаем кастомера в корзине"):
            customer = customer_init.get_customer(token=customer_auth_token)
            assert customer.status_code == 200

            cart_with_customer = self.api_cart.set_customer(
                cart_uuid=cart_uuid, customer=customer.json()
            )
            assert cart_with_customer.json()["data"]["cartUuid"] != None

        with allure.step("Обновляем корзину с методом оплаты cash"):
            cart_with_payment = self.api_cart.update_payment(cart_uuid=cart_uuid, method="cash")
            time.sleep(2)
            assert cart_with_payment.json()["data"]["cartUuid"] != None

        with allure.step("Оформляем заказ"):
            order = self.api_order.send_order(cart_uuid=cart_uuid)
            assert order.status_code == 200
            assert order.json()["data"]["userAuthToken"] is None

        with allure.step("Отправляем запрос на получение заказа через шину"):
            order_status = self.api_esb.esb_check_order(
                cart_with_payment.json()["data"]["order"]["number"]
            )
            assert order_status.status_code == 200

        with allure.step("Проверяем, что в ОМС статус confirmed"):
            assert order_status.json()["order"]["statusId"] == "confirmed"

    @allure.id("2455")
    @allure.title("Оформление заказас софтрегистрацией")
    @allure.description(
        "Проверяем, что заказ омни2 создается в омс с сотфрегистрацией пользователя"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление заказа")
    def test_order_non_authorized_user(self, goods):
        with allure.step("Создаем быструю корзину под неавторизованным пользователем"):
            items = [{"id": goods["qty_2"]["id"], "qty": 1}]
            cart = self.api_cart.create(items=items)
            assert cart.json()["data"]["cartUuid"] != None

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickuppoints.status_code == 200

        with allure.step("Обновляем корзину с доставкой в ПВЗ"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"] != None

        with allure.step("Устанавливаем кастомера в корзине"):
            customer = utils.generate_customer_data()

            cart_with_customer = self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)
            assert cart_with_customer.json()["data"]["cartUuid"] != None

        with allure.step("Обновляем корзину с методом оплаты cash"):
            cart_with_payment = self.api_cart.update_payment(cart_uuid=cart_uuid, method="cash")
            time.sleep(2)
            assert cart_with_payment.json()["data"]["cartUuid"] != None

        with allure.step("Оформляем заказ"):
            order = self.api_order.send_order(cart_uuid=cart_uuid)
            assert order.json()["data"]["paymentMethods"] == "cash"
            assert len(order.json()["data"]["userAuthToken"]) > 0

        with allure.step("Отправляем запрос на получение заказа через шину"):
            order_status = self.api_esb.esb_check_order(
                cart_with_payment.json()["data"]["order"]["number"]
            )
            assert order_status.status_code == 200

        with allure.step("Проверяем, что в ОМС статус confirmed"):
            assert order_status.json()["order"]["statusId"] == "confirmed"
