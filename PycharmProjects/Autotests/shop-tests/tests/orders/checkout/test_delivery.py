import allure
from allure_commons.types import Severity
from befree.api_model.esb import EsbPublic
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.catalog.internal import CatalogInternal
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.catalog.private import CatalogPrivate
from utils.helpers import Helpers
from befree.api_model.orders.public.delivery import shemas
from pytest_voluptuous import S


class TestDelivery(EsbPublic, OrdersPublic, CatalogInternal, QueriesCatalog, CatalogPrivate):
    @allure.id("2463")
    @allure.title("Получение ПВЗ по товару")
    @allure.description(
        "Проверяем, что при отправке запроса ордерс и запроса в омс, получаем одинаковое количество пвз"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_pickpoints_pickup(self):
        with allure.step("Находим товар, который есть в наличии"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=2, store_id=1)
            sku = self.entity_by_id(table="variations", id=variation)["sku"]

        with allure.step("Создаем корзину под неавторизованным пользователем"):
            items = [{"id": variation, "qty": 1}]
            cart = self.api_cart.create(items=items)
            assert cart.status_code == 200

        with allure.step("Отправляем запрос на получение ПВЗ через шину"):
            products = [{"id": sku, "quantity": 1}]
            pickuppoints_from_dwh = self.api_esb.esb_pickuppoints(
                products=products,
                total_item_price=cart.json()["data"]["order"]["calculatedTotal"],
            )
            assert pickuppoints_from_dwh.status_code == 200

        with allure.step("Отправляем запрос на получение ПВЗ в ордерс"):
            pickuppoints_from_orders = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"], methods=["pickup"]
            )
            assert pickuppoints_from_orders.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.pickup) == pickuppoints_from_orders.json()

        with allure.step("Убираем из шины ПВЗ без предоплаты"):
            pickup_without_cod = pickuppoints_from_dwh.json()
            indices = []
            for i in range(len(pickup_without_cod)):
                if (
                    "paymentTypeId" in pickup_without_cod[i]
                    and pickup_without_cod[i]["paymentTypeId"].find("any") == -1
                    and pickup_without_cod[i]["paymentTypeId"].find("prepaid") == -1
                ):
                    indices.append(i)
            for i in sorted(indices, reverse=True):
                del pickup_without_cod[i - 1]

        with allure.step("Сравниваем количество ПВЗ, полученных через шину и через ордерс"):
            orders = list(map(lambda item: item["id"], list(pickuppoints_from_orders.json()["data"])))
            esb = list(map(lambda item: item["id"], list(pickup_without_cod)))
            orders_not_in_esb = list(set(orders) - set(esb))
            esb_not_in_orders = list(set(esb) - set(orders))
            print("orders_not_in_esb", orders_not_in_esb)
            print("esb_not_in_orders", esb_not_in_orders)

            assert len(pickuppoints_from_orders.json()["data"]) == len(pickup_without_cod)

    @allure.id("2465")
    @allure.title("Получение магазинов омни1 по товару")
    @allure.description(
        "Проверяем, что при отправке запроса ордерс и запроса каталога, получаем одинаковое количество магазинов"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_pickpoints_reserveinstore(self):
        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation_in_omni1, store_omni1, store_external_id = self.find_omni_stocks(5)

        with allure.step("Находим город по стору"):
            fias_id, golden_record = self.get_city_by_store(store_id=store_omni1)

        with allure.step("Создаем корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni1, "qty": 5}]
            cart = self.api_cart.create(items=items, fias_id=fias_id, golden_record=golden_record)

        with allure.step("Отправляем запрос на получение магазинов омни1 в ордерс"):
            pickpoints_from_orders = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"],
                fias_id=fias_id,
                golden_record=golden_record,
                methods=["reserveinstore"],
            )
            assert pickpoints_from_orders.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.pickup) == pickpoints_from_orders.json()

        with allure.step("Отправляем запрос на получение магазинов омни1 в каталоге"):
            available_qty = cart.json()["data"]["order"]["itemsQty"]
            items = [{"variationId": variation_in_omni1, "qty": available_qty}]

            pickuppoints_from_catalog = self.api_variations.get_stores_for_variations(fias_id=fias_id, items=items)
            assert pickuppoints_from_catalog.status_code == 200

        with allure.step("Сравниваем количество магазинов омни1, полученных через каталог и через ордерс"):
            assert len(pickpoints_from_orders.json()["data"]) == Helpers().count_value_key_in_list(
                iterable=pickuppoints_from_catalog.json()["data"], key="type", value="retail"
            )

    @allure.id("2462")
    @allure.title("Получение магазинов омни2 по товару")
    @allure.description(
        "Проверяем, что при отправке запроса ордерс и запроса каталога, получаем одинаковое количество магазинов"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_pickpoints_pickupinstore(self):
        with allure.step("Находим товар, который есть в наличии в омни2"):
            variation_in_omni2 = self.find_stocks(store_id=2, qty=2)

        with allure.step("Создаем корзину под неавторизованным пользователем"):
            items = [{"id": variation_in_omni2, "qty": 1}]
            cart = self.api_cart.create(items=items)

        with allure.step("Ищем магазин и включаем у него омни2"):
            store_spb, store_external_id = self.store_by_city(city_id=2)
            response_omni2_on = self.api_stores.update_store(
                store_id=store_spb, city_id=2, pickup_enabled_omni2=1, external_id=store_external_id
            )
            assert response_omni2_on.status_code == 200

        with allure.step("Отправляем запрос на получение магазинов омни2 в ордерс"):
            pickuppoints_from_orders = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"], methods=["pickupinstore"]
            )
            assert pickuppoints_from_orders.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.pickup) == pickuppoints_from_orders.json()

        with allure.step("Отправляем запрос на получение магазинов омни2 в каталоге"):
            available_qty = cart.json()["data"]["order"]["itemsQty"]
            items = [{"variationId": variation_in_omni2, "qty": available_qty}]
            fias_id = "c2deb16a-0330-4f05-821f-1d09c93331e6"
            pickuppoints_from_catalog = self.api_variations.get_stores_for_variations(fias_id=fias_id, items=items)
            assert pickuppoints_from_catalog.status_code == 200

        with allure.step("Сравниваем количество магазинов омни2, полученных через каталог и через ордерс"):
            assert len(pickuppoints_from_orders.json()["data"]) == Helpers().count_value_key_in_list(
                iterable=pickuppoints_from_catalog.json()["data"], key="type", value="3pl"
            )

    @allure.id("2457")
    @allure.title("Получение интервалов по товару")
    @allure.description("")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Оформление доставки")
    def test_intervals(self):
        with allure.step("Находим товар, который есть в наличии"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=2, store_id=1)

        with allure.step("Создаем корзину под неавторизованным пользователем"):
            items = [{"id": variation, "qty": 1}]
            cart = self.api_cart.create(items=items)

        with allure.step("Отправляем запрос на получение интервалов в ордерс"):
            address = {
                "fiasId": "bc8e0d8a-a83c-47d9-9aeb-afeda0c095c1",
                "street": "ул 10-я Красноармейская",
                "building": "д 22",
                "zipcode": "190020",
            }

            intervals_from_orders = self.api_delivery.get_intervals(
                cart_uuid=cart.json()["data"]["cartUuid"],
                address=address,
            )

            assert intervals_from_orders.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.intervals) == intervals_from_orders.json()
