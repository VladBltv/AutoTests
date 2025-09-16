import allure

from befree.api_model.orders.public import OrdersPublic
from befree.api_model.orders.db_queries.queries import QueriesOrders
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders import utils
from befree.api_model.orders.public.order import shemas
from allure_commons.types import Severity
from befree.api_model.customer import Customer
from pytest_voluptuous import S
from mimesis import Person


class TestOrdersHistory(OrdersPublic, QueriesOrders, QueriesCatalog):
    @allure.id("2689")
    @allure.title("Получение истории заказов")
    @allure.description("Проверить, что данные приходят и соответствуют схеме")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "История заказов")
    def test_orders_history(self, goods):
        with allure.step("Авторизуемся под пользователем, у которого есть заказы "):
            email = "melon.test.3@yandex.ru"
            password = "aA123456"

            login_customer = Customer(email=email, password=password).login()
            assert login_customer.status_code == 200
            customer_auth_token_new = login_customer.json()["token"]

        with allure.step("Отправляем запрос на получении истории заказов под этим пользователем"):
            history_response = self.api_order.get_history(token=customer_auth_token_new)
            assert history_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.order_history) == history_response.json()

        with allure.step("Создаем новый заказ для нового пользователя"):
            with allure.step("Формируем данные кастомера"):
                person = Person("en")
                email = person.email()
                password = "aA123456"

            with allure.step("Регистрируем   кастомера и получаем токен"):
                customer_init = Customer(email=email, password=password)
                register_customer = customer_init.register()

                assert register_customer.status_code == 200
                customer_token = register_customer.json()["token"]

            with allure.step("Создаем заказ"):
                items = [{"id": goods["qty_2"]["id"], "qty": 1}]
                utils.create_default_order(items=items, token=customer_token)

        with allure.step("Отправляем запрос на получении истории заказов под этим пользователем"):
            history_response = self.api_order.get_history(token=customer_token)
            assert history_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.order_history) == history_response.json()

    @allure.id("2690")
    @allure.title("Просмотр одного заказа")
    @allure.description("Проверить, что данные приходят и соответствуют схеме")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "История заказов")
    def test_order_get(self):
        with allure.step("Запрос без cartUuid и orderId или с пустыми данными"):
            order_response = self.api_order.get_order(cart_uuid="", order_id="")
            assert order_response.status_code == 422

        with allure.step("Запрос заказа в статусе cart"):
            with allure.step("Находим товар, который есть в наличии"):
                variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(qty=5)

            with allure.step("Создаем корзину под авторизованным пользователем"):
                items = [{"id": variation_in_omni1, "qty": 2}]
                cart_response = self.api_cart.create(items=items)
                assert cart_response.status_code == 200

                cart_uuid = cart_response.json()["data"]["cartUuid"]
                order_id = cart_response.json()["data"]["order"]["id"]

            with allure.step("Запрос заказа"):
                order_response = self.api_order.get_order(cart_uuid=cart_uuid, order_id=order_id)
                assert order_response.status_code == 404

        with allure.step("Запрос заказа c с методом оплаты cash и доставкой pickup"):
            cart_uuid, order_id = self.get_order_by_delivery_payment(payment="cash", shipping="pickup")
            order_response = self.api_order.get_order(cart_uuid=cart_uuid, order_id=order_id)
            assert order_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.order_cash_pickup) == order_response.json()

        with allure.step("Запрос заказа c с методом оплаты podeli и доставкой omni"):
            cart_uuid, order_id = self.get_order_by_delivery_payment(payment="podeli", shipping="reserveinstore")
            order_response = self.api_order.get_order(cart_uuid=cart_uuid, order_id=order_id)
            assert order_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.order_podeli_reserveinstore) == order_response.json()

        with allure.step("Запрос заказа c с методом оплаты sbp и доставкой omni2"):
            cart_uuid, order_id = self.get_order_by_delivery_payment(payment="sbp", shipping="pickupinstore")
            order_response = self.api_order.get_order(cart_uuid=cart_uuid, order_id=order_id)
            assert order_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.order_sbp_pickupinstore) == order_response.json()

        with allure.step("Запрос заказа c с методом оплаты sber и доставкой delivery"):
            cart_uuid, order_id = self.get_order_by_delivery_payment(payment="sber", shipping="delivery")
            order_response = self.api_order.get_order(cart_uuid=cart_uuid, order_id=order_id)
            assert order_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.order_sber_delivery) == order_response.json()
