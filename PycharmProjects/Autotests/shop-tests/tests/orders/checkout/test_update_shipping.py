import allure

from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.catalog.private import CatalogPrivate
from befree.api_model.orders.public.cart import shemas
from befree.api_model.orders import utils
from allure_commons.types import Severity
from pytest_voluptuous import S


class TestUpdateShipping(QueriesCatalog, OrdersPublic, CatalogPrivate):
    @allure.id("2456")
    @allure.title("Обновление быстрой корзины с доставкой омни1")
    @allure.description(
        "Проверяем, что при отправке запроса с доставкой reserveinstore, в ответе приходит reserveinstore"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_shipping_reserveinstore(self):
        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)
            fias_id, golden_record = self.get_city_by_store(store_omni1)

        with ((allure.step("Создаем быструю корзину под неавторизованным пользователем"))):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create_fast_cart(items=items, fias_id=fias_id, golden_record=golden_record,
                                                  current_tab="omni")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with (allure.step("Обновляем корзину с доставкой в магазин омни1")):
            cart_with_shipping = self.api_cart.update_reserveinstore(
                cart_uuid=cart_uuid,
                store_id=store_omni1,
                store_external_id=store_external_id,
                fias_id=fias_id,
                golden_record=golden_record,
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Проверяем, что данные о доставке пришли в ответе запроса"):
            shipping = cart_with_shipping.json()["data"]["order"]["shipping"]
            assert shipping["storeId"] == store_omni1 and shipping["deliveryPrice"] == 0

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.reserveinstore) == shipping

    @allure.id("2466")
    @allure.title("Обновление корзины с доставкой омни2")
    @allure.description(
        "Проверяем, что при отправке запроса с доставкой pickupinstore, в ответе приходит pickupinstore"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_shipping_pickupinstore(self):
        with allure.step("Находим товар, который есть в наличии в омни2"):
            variation_in_omni2 = self.find_stocks(store_id=2, qty=2)

        with (allure.step("Создаем корзину под неавторизованным пользователем")):
            items = [{"id": variation_in_omni2, "qty": 1}]
            cart = self.api_cart.create(items=items)
            assert cart.status_code == 200

            cart_uuid = cart.json()["data"]["cartUuid"]

        with (allure.step("Ищем магазин и включаем у него омни2")):
            store_spb, store_external_id = self.store_by_city(city_id=2)
            response_omni2_on = self.api_stores.update_store(
                store_id=store_spb, city_id=2, pickup_enabled_omni2=1, external_id=store_external_id
            )
            assert response_omni2_on.status_code == 200

        with (allure.step("Обновляем корзину с доставкой в магазин омни2")):
            cart_with_shipping = self.api_cart.update_pickupinstore(
                cart_uuid=cart_uuid, store_id=store_spb, store_external_id=store_external_id
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Проверяем, что данные о доставке пришли в ответе запроса"):
            shipping = cart_with_shipping.json()["data"]["order"]["shipping"]
            assert shipping["storeId"] == store_spb and shipping["deliveryPrice"] == 0

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.pickupinstore) == shipping

    @allure.id("2467")
    @allure.title("Обновление корзины с доставкой в ПВЗ")
    @allure.description(
        "Проверяем, что при отправке запроса с доставкой pickup, в ответе приходит pickup"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_shipping_pickup(self):
        with allure.step("Находим товар, который есть в наличии"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=2, store_id=1)

        with (allure.step("Создаем корзину под неавторизованным пользователем")):
            items = [{"id": variation, "qty": 1}]
            cart = self.api_cart.create(items=items)
            assert cart.status_code == 200

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"], methods=["pickup"]
            )
            assert pickuppoints.status_code == 200

        with (allure.step("Обновляем корзину с доставкой в ПВЗ")):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Проверяем, что данные о доставке пришли в ответе запроса"):
            shipping = cart_with_shipping.json()["data"]["order"]["shipping"]
            assert (
                    shipping["pickpointId"] == pickuppoints.json()["data"][0]["id"]
                    and shipping["deliveryPrice"] == pickuppoints.json()["data"][0]["deliveryPrice"]
            )

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.pickup) == shipping

    @allure.id("2458")
    @allure.title("Обновление корзины с доставкой курьером")
    @allure.description(
        "Проверяем, что при отправке запроса с доставкой delivery, в ответе приходит delivery"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_shipping_delivery(self):
        with allure.step("Находим товар, который есть в наличии"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=2, store_id=1)

        with (allure.step("Создаем корзину под неавторизованным пользователем")):
            items = [{"id": variation, "qty": 1}]
            cart = self.api_cart.create(items=items)

            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный интервал курьера"):
            address = utils.get_address()
            delivery_intervals = self.api_delivery.get_intervals(
                cart_uuid=cart_uuid, address=address["intervals"]
            )
            assert delivery_intervals.status_code == 200

            interval_id = delivery_intervals.json()["data"]["services"][0]["dates"][0]["intervals"][
                0
            ]["id"]
            delivery_price = delivery_intervals.json()["data"]["services"][0]["dates"][0][
                "intervals"
            ][0]["deliveryPrice"]

        with (allure.step("Обновляем корзину с курьерской доставкой")):
            cart_with_shipping = self.api_cart.update_delivery(
                cart_uuid=cart_uuid, interval_id=interval_id, address=address["shipping"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Проверяем, что данные о доставке пришли в ответе запроса"):
            shipping = cart_with_shipping.json()["data"]["order"]["shipping"]
            assert (
                    shipping["intervalId"] == interval_id
                    and shipping["deliveryPrice"] == delivery_price
            )

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.delivery) == shipping

    @allure.title("Обновление обычной корзины с доставкой омни1")
    @allure.description(
        "Проверяем, что при отправке запроса с доставкой reserveinstore, в ответе приходит reserveinstore"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_shipping_reserveinstore(self):
        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)
            fias_id, golden_record = self.get_city_by_store(store_omni1)

        with allure.step("Создаем обычную корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create(items=items, fias_id=fias_id, golden_record=golden_record,)
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Обновляем current_tab в корзине на omni"):
            cart_change_tab = self.api_cart.update_current_tab(cart_uuid=cart_uuid, current_tab="omni", fias_id=fias_id, golden_record=golden_record)
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

        with allure.step("Проверяем, что данные о доставке пришли в ответе запроса"):
            shipping = cart_with_shipping.json()["data"]["order"]["shipping"]
            assert shipping["storeId"] == store_omni1 and shipping["deliveryPrice"] == 0

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.reserveinstore) == shipping