import json
import allure

from befree.api_model import api, db_connection
from mimesis import Person
from requests import Response
from befree.api_model.product import get_undeleted_variation
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders.db_queries.queries import QueriesOrders
from befree.api_model.config.public import ConfigPublic
from befree.api_model.config.private import ConfigPrivate
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.catalog.private import CatalogPrivate
from befree.api_model.config.db_queries.queries import QueriesConfig
from befree.api_model.orders import utils
from allure_commons.types import Severity
from utils import helpers
from pytest_check import check


class TestUpdateCart(
    QueriesCatalog,
    QueriesOrders,
    OrdersPublic,
    CatalogPrivate,
    ConfigPublic,
    ConfigPrivate,
    QueriesConfig,
):
    @allure.id("2448")
    @allure.title("Корзина успешно создается из под города в котором нет магазинов розницы")
    @allure.description(
        "Проверяем, что использование функционала корзины корректно работает для городов, в которых есть только доставка"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_create_cart_in_ebenya(self):
        with allure.step("Берем для теста данные города, которого нет в базе Каталога, например, Можайск"):
            fias_id = "4f86a11c-4258-4859-a227-a79c9ef400ff"
            golden_record = "mozh-344318"
        
        with allure.step("Находим товар, которого нет в наличии нигде"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff=None, qty_omni=None)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, fias_id=fias_id, golden_record=golden_record)

        with allure.step("Проверяем, что ответ от API успешный"):
            check.equal(cart.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что товар попал на вкладку outOfStock и не попал в omni и delivery"):
            tab = cart.json()["data"]["items"]
            check.greater(len(tab["outOfStock"]), 0, "2 Out of stock should be greater than 0")
            check.equal(tab["omni"], [], "3 Omni should be empty")
            check.equal(tab["delivery"], [], "Delivery should be empty")
        
        with allure.step("Находим товар, который есть в наличии только в фф"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1", qty_omni=None)

        with allure.step("Создаем обычную корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, fias_id=fias_id, golden_record=golden_record)
        
        with allure.step("Проверяем, что ответ от API успешный"):
            check.equal(cart.status_code, 200, "Status code should be 200")

        with allure.step("Проверяем, что товар не попал на вкладку outOfStock, а появился на вкладке delivery"):
            tab = cart.json()["data"]["items"]
            check.is_none(tab["outOfStock"], "14 Out of stock should be None")
            check.equal(tab["omni"], [], "15 Omni should be empty")
            check.greater(len(tab["delivery"]), 0, "Delivery should be greater than 0")

    @allure.id("2449")
    @allure.title("Обработка несуществующего товара в корзине")
    @allure.description(
        "При попытке добавить в корзину несуществующий товар или при получении корзины, в котором товар стал несуществующим, такой товар не добавляется / удаляется из корзины"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_processing_unexisting_product_in_cart(self):
        # Кейс работает при выключенном кеше
        with allure.step("Добавление в корзину несуществующего варианта"):
            with allure.step("Определяем заведомо не существующий вариант, к последнему по id варианту добавляем 1"):
                query = """
                        select  v.id
                        from variations v
                        order by v.id desc
                        limit 1
                    """
                data = db_connection.catalog.get_data(query)
                last_variant = data[0]["id"]
                unexisting_variant = last_variant + 1

            with allure.step("Создаем корзину с заведомо несуществующим товаром"):
                items = [{"id": unexisting_variant, "qty": 5}]
                cart = self.api_cart.create(items=items)

            with allure.step("Запрос возвращает ошибку 422: Variation not found"):
                cart.status_code == 422

        with allure.step("Получение корзины, товар в которой был удален"):
            product = variant = {}
            (
                product["id"],
                product["article"],
                variant["id"],
                variant["sku"],
            ) = get_undeleted_variation()

            with allure.step("Добавляем в корзину существующий товар"):
                items = [{"id": variant["id"], "qty": 5}]
                create_response = self.api_cart.create(items=items)

            with allure.step("Корзина создается успешно, товар добавлен в корзину"):
                create_response.status_code == 200
                cart_uuid = create_response.json()["data"]["cartUuid"]
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert json.dumps(cart_data).find(str(variant["id"])) != -1

            with allure.step("Удаляем вариант"):
                response = self.api_products.delete_variation(product_id=product["id"], variation_id=variant["id"])
                assert response.status_code == 200

            with allure.step("Запрашиваем корзину"):
                get_response = self.api_cart.get(cart_uuid=cart_uuid)
                assert get_response.status_code == 200

            with allure.step("Получаем данные по корзине из API"):
                cart_get_response = self.api_cart.get(cart_uuid=cart_uuid)

            with allure.step("Проверяем, что товар не выводится ни в одной из вкладок в ответе корзины"):
                assert variant["id"] not in cart_get_response.json()["data"]["items"]

            with allure.step("Восстанавливаем удаленный товар"):
                response: Response = api.private_session.patch(
                    url=f"/products/{product['id']}/variations/{variant['id']}",
                )
                assert response.status_code == 200

    @allure.id("1311")
    @allure.title("Обнуление товара по обеим вкладкам корзины")
    @allure.label("service", "Orders")
    @allure.feature("Создание и изменение корзины")
    @allure.label("suite", "Cart")
    @allure.label("owner", "potegovaav")
    def test_reset_goods(self):
        with allure.step("Добавить в корзину товар в наличии и в фф и омни"):
            items = [{"id": 228890, "qty": 1}]
            cart_create_response = self.api_cart.create(items=items)
            cart_uuid = cart_create_response.json()["data"]["cartUuid"]

            with allure.step("Для каждой вкладки установлено количество 1"):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 1 and cart_data["items"][0]["qtyDelivery"] == 1

        with allure.step("Обнулить товар для вкладки omni "):
            items = [{"id": 228890, "qty": 0}]
            cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="omni", items=items)
            assert cart_response.status_code == 200

            with allure.step("Состав корзины delivery=1, omni=0"):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 0 and cart_data["items"][0]["qtyDelivery"] == 1

        with allure.step("Обнулить товар для вкладки delivery"):
            items = [{"id": 228890, "qty": 0}]
            cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
            assert cart_response.status_code == 200

            with allure.step("Товар полностью удаляется из сущности корзины"):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert json.dumps(cart_data).find("228890") == -1

    @allure.id("1324")
    @allure.title("Товар обнуленный на одной из вкладок корзины можно восстановить")
    @allure.label("service", "Orders")
    @allure.feature("Создание и изменение корзины")
    @allure.label("suite", "Cart")
    @allure.label("owner", "potegovaav")
    def test_restore_reset_goods(self):
        with allure.step("Кейс 1"):
            with allure.step("Находим товар, который есть в наличии в омни1"):
                (
                    variation_in_omni1,
                    store_omni1,
                    store_external_id,
                ) = self.find_omni_stocks(5)
                fias_id, golden_record = self.get_city_by_store(store_omni1)
                items = [{"id": variation_in_omni1, "qty": 1}]

            with allure.step("Состояние: товар есть на обеих вкладках в количестве delivery 1 / omni 1"):
                cart_create_response = self.api_cart.create(items=items, fias_id=fias_id, golden_record=golden_record)
                cart_uuid = cart_create_response.json()["data"]["cartUuid"]

            with allure.step("Изменить количество на delivery 2 / omni 1"):
                items = [{"id": variation_in_omni1, "qty": 2}]
                cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
                assert cart_response.status_code == 200

                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyDelivery"] == 2

            with allure.step("Обнулить на вкладке omni"):
                items = [{"id": variation_in_omni1, "qty": 0}]
                cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="omni", items=items)
                assert cart_response.status_code == 200

                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 0

            with allure.step("Восстановить на вкладке omni"):
                items = [{"id": variation_in_omni1, "qty": 1}]
                cart_response = self.api_cart.restore_qty(cart_uuid=cart_uuid, current_tab="omni", items=items)
                assert cart_response.status_code == 200

            with allure.step(
                "Товар восстанавливается на вкладке omni в количестве 1шт. На вкладке delivery количество не меняется"
            ):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 1 and cart_data["items"][0]["qtyDelivery"] == 2

            with allure.step("Обнулить на вкладке delivery"):
                items = [{"id": variation_in_omni1, "qty": 0}]
                cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
                assert cart_response.status_code == 200

                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyDelivery"] == 0

            with allure.step("Восстановить на вкладке delivery"):
                items = [{"id": variation_in_omni1, "qty": 2}]
                cart_response = self.api_cart.restore_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
                assert cart_response.status_code == 200

            with allure.step(
                "Товар восстанавливается на вкладке delivery в переданном количестве. На вкладке omni количество не меняется"
            ):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 1 and cart_data["items"][0]["qtyDelivery"] == 2

        with allure.step("Кейс 2"):
            items = [{"id": variation_in_omni1, "qty": 1}]

            with allure.step("Состояние: товар есть на обеих вкладках в количестве delivery 1 / omni 1"):
                cart_create_response = self.api_cart.create(items=items)
                assert cart_response.status_code == 200
                cart_uuid = cart_create_response.json()["data"]["cartUuid"]

            with allure.step("Обнулить товар на вкладке omni"):
                items = [{"id": variation_in_omni1, "qty": 0}]
                cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="omni", items=items)
                assert cart_response.status_code == 200

                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 0

            with allure.step("Провести операцию восстановления для вкладки delivery"):
                items = [{"id": variation_in_omni1, "qty": 1}]
                cart_response = self.api_cart.restore_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
                assert cart_response.status_code == 200

            with allure.step("Состояние корзины не изменяется"):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 0 and cart_data["items"][0]["qtyDelivery"] == 1

        with allure.step("Кейс 3"):
            items = [{"id": variation_in_omni1, "qty": 1}]

            with allure.step("Состояние: товар есть на обеих вкладках в количестве delivery 1 / omni 1"):
                cart_create_response = self.api_cart.create(items=items)
                cart_uuid = cart_create_response.json()["data"]["cartUuid"]

            with allure.step("Обнулить товар по обеим вкладкам"):
                items = [{"id": variation_in_omni1, "qty": 0}]
                cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="omni", items=items)
                assert cart_response.status_code == 200

                cart_response = self.api_cart.update_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
                assert cart_response.status_code == 200

            with allure.step("Товар уходит из корзины"):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert json.dumps(cart_data).find(f"{variation_in_omni1}") == -1

            with allure.step("Провести оперцию restore над любой из вкладок"):
                items = [{"id": variation_in_omni1, "qty": 1}]
                cart_response = self.api_cart.restore_qty(cart_uuid=cart_uuid, current_tab="delivery", items=items)
                assert cart_response.status_code == 200

            with allure.step("Товар восстанавливается только в данной вкладке"):
                cart_data = self.get_cart_data(cart_uuid)[0]["data"]
                assert cart_data["items"][0]["qtyOmni"] == 0 and cart_data["items"][0]["qtyDelivery"] == 1

    @allure.id("2447")
    @allure.title("Проверка валидации параметра state")
    @allure.description("Проверяем, что при разных условиях срабатывает проверка на валидацию")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_validation_state(self):
        with allure.step("Находим товар, который есть в наличии"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=2, store_id=1)

        with allure.step("Создаем корзину под неавторизованным пользователем"):
            items = [{"id": variation, "qty": 1}]
            cart = self.api_cart.create(items=items)
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickuppoints.status_code == 200
            pickuppoint_id = pickuppoints.json()["data"][0]["id"]

        with allure.step("Обновляем корзину с доставкой в ПВЗ с state = cart"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoint_id, state="cart"
            )
            with allure.step("Проверяем, что запрос не прошел валидацию"):
                assert cart_with_shipping.json()["data"]["notifications"][0]["level"] == "error"

        with allure.step("Обновляем корзину с оплатой с state = cart"):
            cart_with_payment = self.api_cart.update_payment(cart_uuid=cart_uuid, method="sber", state="cart")
            with allure.step("Проверяем, что запрос не прошел валидацию"):
                assert cart_with_payment.json()["data"]["notifications"][0]["level"] == "error"

        with allure.step("Обновляем корзину с доставкой в ПВЗ с state = checkout"):
            cart_with_shipping = self.api_cart.update_pickup(cart_uuid=cart_uuid, pickpoint_id=pickuppoint_id)
            with allure.step("Проверяем, что запрос прошел успешно"):
                assert cart_with_shipping.json()["data"]["cartUuid"] == cart_uuid

        with allure.step("Обновляем корзину с промокодом с state = checkout"):
            cart_with_promocode = self.api_cart.update_promocode(
                cart_uuid=cart_uuid, promocode="123456", state="checkout"
            )
            with allure.step("Проверяем, что запрос не прошел валидацию"):
                assert cart_with_promocode.status_code == 422

        with allure.step("Обновляем количество товаров в корзине на state = checkout"):
            cart_with_item = self.api_cart.update_qty(
                cart_uuid=cart_uuid, current_tab="delivery", items=[{"id": variation, "qty": 1}]
            )

            with allure.step("Проверяем, что запрос не прошел валидацию"):
                assert cart_with_item.status_code == 422

        with allure.step("Восстанавливаем товар в корзине на state = checkout"):
            cart_with_item = self.api_cart.restore_qty(
                cart_uuid=cart_uuid, current_tab="delivery", items=[{"id": variation, "qty": 1}]
            )
            with allure.step("Проверяем, что запрос не прошел валидацию"):
                assert cart_with_item.status_code == 422

        with allure.step("Устанавливаем кастомера в корзину"):
            person = Person("en")
            customer = dict()
            customer["email"] = person.email()
            customer["first_name"] = person.first_name()
            customer["last_name"] = person.last_name()

            cart_with_customer = self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)
            with allure.step("Проверяем, что запрос прошел валидацию"):
                assert cart_with_customer.json()["data"]["cartUuid"] == cart_uuid

        with allure.step("Обновляем корзину с оплатой с state = summary"):
            cart_with_payment = self.api_cart.update_payment(cart_uuid=cart_uuid, method="sber")
            with allure.step("Проверяем, что запрос прошел успешно"):
                assert cart_with_payment.json()["data"]["cartUuid"] == cart_uuid

        with allure.step("Меняем в корзине state = cart"):
            cart_state_cart = self.api_cart.update_state(cart_uuid=cart_uuid, state="cart")
            assert cart_state_cart.json()["data"]["cartUuid"] == cart_uuid

        with allure.step("Проверяем, что сбросились данные по доставке полностью"):
            assert (
                cart_state_cart.json()["data"]["order"]["payment"] is None
                and cart_state_cart.json()["data"]["order"]["shipping"] is None
            )

    @allure.id("2732")
    @allure.title("Очистка данных доставки при изменении стейта")
    @allure.description(
        "Проверяем логику очистки данных по доставке в корзине с учетом изменения стейта и примерения управляющего флага"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    @allure.description(
        """Для более гибкого управления логикой очистки данных введен флаг stateModifier, 
        который в сочетании с изменнием стейта может как удалять, так и сохранять данные по доставке """
    )
    def test_clear_shipping(self):
        fias_id = "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"
        golden_record = "mosk-941139"

        with allure.step("Создать корзину под неавторизованным пользователем для проверок FF"):
            with allure.step("Находим товар, который есть в наличии"):
                variation = self.find_omniAndSf_stocks(qty=3, city_id=2, store_id=1)
                items = [{"id": variation, "qty": 1}]

            cart_create_response = self.api_cart.create(items=items, fias_id=fias_id, golden_record=golden_record)
            cart_uuid = cart_create_response.json()["data"]["cartUuid"]

        with allure.step("Подготовить данные для получателя"):
            person = Person("en")
            customer = dict()
            customer["email"] = person.email()
            customer["first_name"] = person.first_name()
            customer["last_name"] = person.last_name()

        with allure.step("Подготовить данные для доставки курьером"):
            address = utils.get_address(city_fias_id=fias_id, street="оран", building="2")
            intervals_response = self.api_delivery.get_intervals(
                cart_uuid=cart_uuid,
                fias_id=fias_id,
                golden_record=golden_record,
                address=address["intervals"],
            )
            interval_id = intervals_response.json()["data"]["services"][0]["dates"][0]["intervals"][0]["id"]

        with allure.step("Подготовить данные для доставки через ПВЗ"):
            orders_pickuppoints_response = self.api_delivery.get_pickpoints(
                cart_uuid=cart_uuid,
                fias_id=fias_id,
                golden_record=golden_record,
                methods=["pickup"],
            )
            pickpoint = orders_pickuppoints_response.json()["data"][0]

        with allure.step("Параметр stateModifier нельзя передавать со стейтом cart"):
            with allure.step("Передать stateModifier со state=cart"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="cart",
                    stateModifier="dontClearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что бэк выдает ошибку"):
                assert cart_update_state_response.status_code != 200
                assert "stateModifier" in cart_update_state_response.json()["errors"]["stateModifier"][0]

        with allure.step("При переходе со стейта checkout на стейт cart в корзине shipping сбрасывается в null"):
            with allure.step("Добавить в корзину данные по доставке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что поле shipping в корзине не null"):
                assert update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Обновить стейт с checkout на cart без модификатора"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="cart",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что поле shipping в корзине стало null, customer корзине стало null"):
                assert cart_update_state_response.json()["data"]["order"]["shipping"] is None

        with allure.step(
            "Если state не меняется  checkout -> checkout и stateModifier = null/не передан, то данные по доставке сохраняются "
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Обновить стейт checkout -> checkout и stateModifier = null"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier=None,
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

            with allure.step("Обновить стейт checkout -> checkout и stateModifier не передан"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

        with allure.step(
            "Если state не меняется  checkout -> checkout и stateModifier = clearCheckout, то данные по доставке очищаются частично: "
            "остается метод доставки и адрес для курьера, все id очищаются "
        ):
            with allure.step("Добавить в корзину данные по доставке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что поле shipping в корзине не null"):
                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

                assert shipping_before_update_state is not None

            with allure.step("Обновить стейт checkout -> checkout и stateModifier = clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state_1 = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что shipping после апдейта не null, сохранен метод доставки и адрес, intreval_id очищен"
            ):
                assert shipping_after_update_state_1 is not None
                assert shipping_after_update_state_1["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state_1["address"] == shipping_before_update_state["address"]
                assert shipping_after_update_state_1["intervalId"] is None

        with allure.step(
            "Если state не меняется  checkout -> checkout и stateModifier = dontClearCheckout, то данные по доставке не очищаются"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Обновить стейт checkout -> checkout и stateModifier = dontClearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="dontClearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

        with allure.step(
            "Если state меняется  checkout -> summary и stateModifier в любом значении кроме null, то апи выдает ошибку"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить стейт checkout -> summary и stateModifier = clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что бэк выдает ошибку"):
                assert cart_update_state_response.status_code != 200
                assert "stateModifier" in cart_update_state_response.json()["errors"]["stateModifier"][0]

        with allure.step(
            "Если state меняется  checkout -> summary и stateModifier отсутствует, то данные по доставке сохраняются"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить стейт checkout -> summary и stateModifier отсутствует"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

        with allure.step(
            "Если state меняется  summary -> cart и stateModifier не передан то shipping и customer сбрасывается в null"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid, state="cart", fias_id=fias_id, golden_record=golden_record
                )

                self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на cart"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid, state="cart", fias_id=fias_id, golden_record=golden_record
                )

            with allure.step("Проверить, что shipping сбрасывается в null"):
                assert cart_update_state_response.json()["data"]["order"]["shipping"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is None

        with allure.step(
            "Если state меняется  summary -> checkout и stateModifier не передан или null, "
            "то в shipping очищаются id, остается тип доставки и адрес для курьера, customer не очищается"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid, state="cart", fias_id=fias_id, golden_record=golden_record
                )

                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary "):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на checkout без передачи stateModifier"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что тип доставки не обнулился, но сбросились id ПВЗ"):
                assert shipping_after_update_state is not None
                assert shipping_after_update_state["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state["pickpointId"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

            with allure.step("Добавить данные по достаке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на checkout с stateModifier=null"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier=None,
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state_2 = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что shipping после апдейта не null, сохранен метод доставки и адрес, intreval_id очищен"
            ):
                assert shipping_after_update_state_2 is not None
                assert shipping_after_update_state_2["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state_2["address"] == shipping_before_update_state["address"]
                assert shipping_after_update_state_2["intervalId"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

        with allure.step(
            "Если state меняется  summary -> checkout и stateModifier = clearCheckout "
            "то в shipping очищаются id, остается тип доставки и адрес для курьера, данные по customer сохраняются"
        ):
            with allure.step("Добавить данные по достаке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на checkout с stateModifier=clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state_3 = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что shipping после апдейта не null, сохранен метод доставки и адрес, intreval_id очищен"
            ):
                assert shipping_after_update_state_3 is not None
                assert shipping_after_update_state_3["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state_3["address"] == shipping_before_update_state["address"]
                assert shipping_after_update_state_3["intervalId"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

        with allure.step(
            "Если state меняется  summary -> checkout и stateModifier = dontClearCheckout то shipping остается как был"
        ):
            with allure.step("Добавить данные по достаке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на cart с stateModifier=dontClearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="dontClearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что shipping после апдейта не изменился, кастомер не сбросился"):
                assert shipping_before_update_state == shipping_after_update_state
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

    @allure.id("2732")
    @allure.title("Очистка данных доставки при изменении стейта для быстрой корзины")
    @allure.description(
        "Проверяем логику очистки данных по доставке в быстрой корзине с учетом изменения стейта и примерения "
        "управляющего флага"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    @allure.description(
        """Для более гибкого управления логикой очистки данных введен флаг stateModifier, 
        который в сочетании с изменнием стейта может как удалять, так и сохранять данные по доставке """
    )
    def test_clear_shipping_quick_cart(self):
        fias_id = "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"
        golden_record = "mosk-941139"

        with allure.step("Создать корзину под неавторизованным пользователем для проверок SFS"):
            with allure.step("Находим товар, который есть в наличии"):
                variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None)
                items = [{"id": variation[0]["variation_id"], "qty": 1}]

            cart_create_response = self.api_cart.create_fast_cart(
                items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden_record
            )
            assert cart_create_response.json()["data"]["cartUuid"]

            cart_uuid = cart_create_response.json()["data"]["cartUuid"]

        with allure.step("Подготовить данные для получателя"):
            person = Person("en")
            customer = dict()
            customer["email"] = person.email()
            customer["first_name"] = person.first_name()
            customer["last_name"] = person.last_name()

        with allure.step("Подготовить данные для доставки курьером"):
            address = utils.get_address(city_fias_id=fias_id, street="оран", building="2")
            intervals_response = self.api_delivery.get_intervals(
                cart_uuid=cart_uuid,
                fias_id=fias_id,
                golden_record=golden_record,
                address=address["intervals"],
            )
            interval_id = intervals_response.json()["data"]["services"][0]["dates"][0]["intervals"][0]["id"]

        with allure.step("Подготовить данные для доставки через ПВЗ"):
            orders_pickuppoints_response = self.api_delivery.get_pickpoints(
                cart_uuid=cart_uuid,
                fias_id=fias_id,
                golden_record=golden_record,
                methods=["pickup"],
            )
            pickpoint = orders_pickuppoints_response.json()["data"][0]

        with allure.step("Подготовить корзину и данные для доставки через ОМНИ"):
            variation = self.find_variation_by_availability_condition(
                qty_omni="> 1", qty_sfs=None, qty_ff=None, city_id_in=6, limit=2
            )
            items_2 = [
                {"id": variation[0]["variation_id"], "qty": 1},
                {"id": variation[1]["variation_id"], "qty": 1},
            ]

            cart_create_response_2 = self.api_cart.create_fast_cart(
                items=items_2, fias_id=fias_id, golden_record=golden_record, current_tab="omni"
            )
            cart_uuid_2 = cart_create_response_2.json()["data"]["cartUuid"]

            orders_pickuppoints_response = self.api_delivery.get_pickpoints(
                cart_uuid=cart_uuid_2,
                fias_id=fias_id,
                golden_record=golden_record,
                methods=["reserveinstore"],
            )
            omni_stores = orders_pickuppoints_response.json()["data"]
            omni_store = dict()
            for store in omni_stores:
                if len(store["items"]) < len(items_2):
                    omni_store = store
                    break

        with allure.step("Параметр stateModifier нельзя передавать со стейтом cart"):
            with allure.step("Передать stateModifier со state=cart"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="cart",
                    stateModifier="dontClearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что бэк выдает ошибку"):
                assert cart_update_state_response.status_code != 200
                assert "stateModifier" in cart_update_state_response.json()["errors"]["stateModifier"][0]

        with allure.step("При переходе со стейта checkout на стейт cart в корзине shipping сбрасывается в null"):
            with allure.step("Добавить в корзину данные по доставке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что поле shipping в корзине не null"):
                assert update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Обновить стейт с checkout на cart без модификатора"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="cart",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что поле shipping в корзине стало null, customer корзине стало null"):
                assert cart_update_state_response.json()["data"]["order"]["shipping"] is None

        with allure.step(
            "Если state не меняется  checkout -> checkout и stateModifier = null/не передан, то данные по доставке сохраняются "
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Обновить стейт checkout -> checkout и stateModifier = null"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier=None,
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

            with allure.step("Обновить стейт checkout -> checkout и stateModifier не передан"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

        with allure.step(
            "Если state не меняется  checkout -> checkout и stateModifier = clearCheckout, то данные по доставке очищаются частично: "
            "остается метод доставки и адрес для курьера, все id очищаются "
        ):
            with allure.step("Добавить в корзину данные по доставке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что поле shipping в корзине не null"):
                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

                assert shipping_before_update_state is not None

            with allure.step("Обновить стейт checkout -> checkout и stateModifier = clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state_1 = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что shipping после апдейта не null, сохранен метод доставки и адрес, intreval_id очищен"
            ):
                assert shipping_after_update_state_1 is not None
                assert shipping_after_update_state_1["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state_1["address"] == shipping_before_update_state["address"]
                assert shipping_after_update_state_1["intervalId"] is None

        with allure.step(
            "Если state не меняется  checkout -> checkout и stateModifier = dontClearCheckout, то данные по доставке не очищаются"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Обновить стейт checkout -> checkout и stateModifier = dontClearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="dontClearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

        with allure.step(
            "Если state меняется  checkout -> summary и stateModifier в любом значении кроме null, то апи выдает ошибку"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить стейт checkout -> summary и stateModifier = clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Проверить, что бэк выдает ошибку"):
                assert cart_update_state_response.status_code != 200
                assert "stateModifier" in cart_update_state_response.json()["errors"]["stateModifier"][0]

        with allure.step(
            "Если state меняется  checkout -> summary и stateModifier отсутствует, то данные по доставке сохраняются"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить стейт checkout -> summary и stateModifier отсутствует"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что в шиппинге все данные сохранены"):
                assert shipping_before_update_state == shipping_after_update_state

        with allure.step(
            "Если state меняется  summary -> cart и stateModifier не передан то shipping и customer сбрасывается в null"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid, state="cart", fias_id=fias_id, golden_record=golden_record
                )

                self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на cart"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid, state="cart", fias_id=fias_id, golden_record=golden_record
                )

            with allure.step("Проверить, что shipping сбрасывается в null"):
                assert cart_update_state_response.json()["data"]["order"]["shipping"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is None

        with allure.step(
            "Если state меняется  summary -> checkout и stateModifier не передан или null, "
            "то в shipping очищаются id, остается тип доставки и адрес для курьера, customer не очищается"
        ):
            with allure.step("Добавить в корзину данные по доставке через ПВЗ"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid, state="cart", fias_id=fias_id, golden_record=golden_record
                )

                update_shipping_pickup_response = self.api_cart.update_pickup(
                    cart_uuid=cart_uuid,
                    pickpoint_id=pickpoint["id"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_pickup_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary "):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на checkout без передачи stateModifier"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что тип доставки не обнулился, но сбросились id ПВЗ"):
                assert shipping_after_update_state is not None
                assert shipping_after_update_state["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state["pickpointId"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

            with allure.step("Добавить данные по достаке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на checkout с stateModifier=null"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier=None,
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state_2 = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что shipping после апдейта не null, сохранен метод доставки и адрес, intreval_id очищен"
            ):
                assert shipping_after_update_state_2 is not None
                assert shipping_after_update_state_2["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state_2["address"] == shipping_before_update_state["address"]
                assert shipping_after_update_state_2["intervalId"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

        with allure.step(
            "Если state меняется  summary -> checkout и stateModifier = clearCheckout "
            "то в shipping очищаются id, остается тип доставки и адрес для курьера, данные по customer сохраняются"
        ):
            with allure.step("Добавить данные по достаке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на checkout с stateModifier=clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state_3 = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что shipping после апдейта не null, сохранен метод доставки и адрес, intreval_id очищен"
            ):
                assert shipping_after_update_state_3 is not None
                assert shipping_after_update_state_3["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state_3["address"] == shipping_before_update_state["address"]
                assert shipping_after_update_state_3["intervalId"] is None
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

        with allure.step(
            "Если state меняется  summary -> checkout и stateModifier = dontClearCheckout то shipping остается как был"
        ):
            with allure.step("Добавить данные по достаке курьером"):
                update_shipping_delivery_response = self.api_cart.update_delivery(
                    cart_uuid=cart_uuid,
                    interval_id=interval_id,
                    address=address["shipping"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                shipping_before_update_state = update_shipping_delivery_response.json()["data"]["order"]["shipping"]

            with allure.step("Добавить данные по получателю"):
                self.api_cart.set_customer(cart_uuid=cart_uuid, customer=customer)

            with allure.step("Обновить статус на summary"):
                self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="summary",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

            with allure.step("Обновить статус на cart с stateModifier=dontClearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid,
                    state="checkout",
                    stateModifier="dontClearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step("Проверить, что shipping после апдейта не изменился, кастомер не сбросился"):
                assert shipping_before_update_state == shipping_after_update_state
                assert cart_update_state_response.json()["data"]["order"]["customer"] is not None

        with allure.step(
            "Для заказа омни1 если state меняется  checkout -> checkout и stateModifier = clearCheckout "
            "и после очистки меняется состав заказа, то АПИ отрабатывает без ошибок, восстанавливается прежний состав заказа"
        ):
            with allure.step("Обновляем текущую вкладку на omni. В заказе два товара."):
                update_current_tab_response = self.api_cart.update_current_tab(
                    cart_uuid=cart_uuid_2,
                    current_tab="omni",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )
                initial_order_list_len = len(update_current_tab_response.json()["data"]["order"]["items"])
                assert initial_order_list_len == 2

            with allure.step(
                "Добавить данные по магазину в котором в наличии только один товар. В заказе остается один товар"
            ):
                update_shipping_reserveinstore_response = self.api_cart.update_reserveinstore(
                    cart_uuid=cart_uuid_2,
                    store_id=omni_store["id"],
                    store_external_id=omni_store["externalId"],
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                order_list_len_after_update_shipping = len(
                    update_shipping_reserveinstore_response.json()["data"]["order"]["items"]
                )
                assert order_list_len_after_update_shipping == 1

                shipping_before_update_state = update_shipping_reserveinstore_response.json()["data"]["order"][
                    "shipping"
                ]

            with allure.step("Обновить статус checkout -> checkout с stateModifier=clearCheckout"):
                cart_update_state_response = self.api_cart.update_state(
                    cart_uuid=cart_uuid_2,
                    state="checkout",
                    stateModifier="clearCheckout",
                    fias_id=fias_id,
                    golden_record=golden_record,
                )

                order_list_len_after_update_state = len(cart_update_state_response.json()["data"]["order"]["items"])
                shipping_after_update_state = cart_update_state_response.json()["data"]["order"]["shipping"]

            with allure.step(
                "Проверить, что запрос отрабатывает без ошибок shipping после апдейта не null, сохранен метод доставки, "
                "id магазина очищен, восстановился прежний состав заказа"
            ):
                assert cart_update_state_response.status_code == 200
                assert order_list_len_after_update_state == initial_order_list_len
                assert shipping_after_update_state is not None
                assert shipping_after_update_state["method"] == shipping_before_update_state["method"]
                assert shipping_after_update_state["storeId"] is None
                assert shipping_after_update_state["storeExternalId"] is None

    @allure.id("2452")
    @allure.title("Проверка работы установленного трешхолда на максимальное количества товара в корзине")
    @allure.description("Проверяем, что при разных значениях отрабатывает корректно")
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_cart_maxOrderItemsCount(self):
        with allure.step("Изменяем значение maxOrderItemsCount"):
            key = "maxOrderItemsCount"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи на 5 штук"):
                value = 5
                configs_response = self.api_private_config.update_single(
                    title=config_bd[0]["title"], key=key, value=value
                )
                assert configs_response.status_code == 204

        with allure.step("Находим товар, который есть в наличии в фф количестве более 5 штук"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 5")

        with allure.step("Создаем обычную корзину с этим вариантов в количестве 5 штук"):
            items = [{"id": variation[0]["variation_id"], "qty": 5}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]

        with allure.step("Проверяем, что не пришло предупреждение о максимальном количестве товаров"):
            assert cart.json()["data"]["notifications"] is None

        with allure.step("Создаем обычную корзину с этим вариантов в количестве 6 штук"):
            items = [{"id": variation[0]["variation_id"], "qty": 6}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]

        with allure.step("Проверяем, что предупреждение о максимальном количестве товаров пришло"):
            assert cart.json()["data"]["notifications"][0]["level"] == "error"

    @allure.id("2451")
    @allure.title("Трешхолд на бесплатную доставку в обычной корзине")
    @allure.description(
        "Для обычной корзины используется свой трешхолд. Данные по нему получаются из конфигов по "
        "ключу freeShippingSum. Трешхолд используется только для методов доставок курьером и ПВЗ"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_cart_trashhold(self):
        with allure.step("Находим товар, который есть в наличии в фф"):
            variation = self.find_variation_by_availability_condition(qty_sfs=None, qty_ff="> 1")

        with allure.step("Создаем обычную корзину с этим вариантов"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items)
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Изменяем значение трешхолда freeShippingSum"):
            key = "freeShippingSum"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи"):
                freeShippingSum_value = cart.json()["data"]["order"]["calculatedTotal"]
                configs_response = self.api_private_config.update_single(
                    title=config_bd[0]["title"], key=key, value=freeShippingSum_value
                )
                assert configs_response.status_code == 204

        with allure.step("Получаем созданную корзину с суммой товаров = трешолду"):
            cart = self.api_cart.get(cart_uuid=cart_uuid)
            assert cart.json()["data"]["cartUuid"]

        with allure.step("Проверяем, leftToTreshold = 0"):
            assert cart.json()["data"]["order"]["leftToTreshold"] == 0

        with allure.step("Отправляем запрос на получение методов доставки"):
            delivery_methods_response = self.api_delivery.get_delivery_methods(cart_uuid=cart_uuid)
            assert delivery_methods_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки равна 0"):
            assert delivery_methods_response.json()["data"][0]["price"] == 0
            assert delivery_methods_response.json()["data"][1]["price"] == 0

        with allure.step("Отправляем запрос на получение списка пвз"):
            pickpoints_response = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickpoints_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем пвз равна 0"):
            count_pickpoints = helpers.count_value_key_in_list(
                iterable=pickpoints_response.json()["data"], key="deliveryPrice", value=0
            )
            assert len(pickpoints_response.json()["data"]) == count_pickpoints

        with allure.step("Отправляем запрос на получение списка интервалов"):
            address = utils.get_address()
            intervals_response = self.api_delivery.get_intervals(cart_uuid=cart_uuid, address=address["intervals"])
            assert intervals_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем интервалам равна 0"):
            assert intervals_response.json()["data"]["services"][0]["priceMin"] == 0
            assert intervals_response.json()["data"]["services"][1]["priceMin"] == 0

        with allure.step("Изменяем сумму трешхолда на +1"):
            with allure.step("Изменяем значение по ключу через апи"):
                freeShippingSum_value = freeShippingSum_value + 1
                configs_response = self.api_private_config.update_single(
                    title=config_bd[0]["title"], key=key, value=freeShippingSum_value
                )
                assert configs_response.status_code == 204

        with allure.step("Получаем созданную корзину с суммой товаров = трешолду +1"):
            cart = self.api_cart.get(cart_uuid=cart_uuid)
            assert cart.json()["data"]["cartUuid"]

        with allure.step("Проверяем, leftToTreshold = 1"):
            assert cart.json()["data"]["order"]["leftToTreshold"] == 1

        with allure.step("Отправляем запрос на получение методов доставки"):
            delivery_methods_response = self.api_delivery.get_delivery_methods(cart_uuid=cart_uuid)
            assert delivery_methods_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки больше 0"):
            omni2_enabled = self.entity_by_id(table="cities", id=2)["omni_2"]
            if omni2_enabled:
                assert delivery_methods_response.json()["data"][0]["price"] >= 0
                assert delivery_methods_response.json()["data"][1]["price"] > 0
            else:
                assert delivery_methods_response.json()["data"][0]["price"] > 0
                assert delivery_methods_response.json()["data"][1]["price"] > 0

        with allure.step("Отправляем запрос на получение списка пвз"):
            pickpoints_response = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickpoints_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем пвз > 0"):
            count_pickpoints = helpers.count_value_key_in_list(
                iterable=pickpoints_response.json()["data"], key="deliveryPrice", value=0
            )
            assert count_pickpoints == 0

        with allure.step("Отправляем запрос на получение списка интервалов"):
            address = utils.get_address()
            intervals_response = self.api_delivery.get_intervals(cart_uuid=cart_uuid, address=address["intervals"])
            assert intervals_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем интервалам больше 0"):
            assert intervals_response.json()["data"]["services"][0]["priceMin"] > 0
            assert intervals_response.json()["data"]["services"][1]["priceMin"] > 0

    @allure.id("2730")
    @allure.title("Трешхолд на бесплатную доставку в быстрой корзине")
    @allure.description(
        "Для быстрой корзины используется свой трешхолд. Данные по нему получаются из конфигов по "
        "ключу sfsFreeShippingSum. Трешхолд используется только для методов доставок курьером и ПВЗ"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "Создание и изменение корзины")
    def test_quick_cart_trashhold(self):
        with allure.step("Находим товар, который есть в наличии в сфс"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None)

        with allure.step("Создаем быструю корзину с этим вариантов"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Изменяем значение sfsFreeShippingSum"):
            key = "sfsFreeShippingSum"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи"):
                sfsFreeShippingSum_value = cart.json()["data"]["order"]["calculatedTotal"]
                configs_response = self.api_private_config.update_single(
                    title=config_bd[0]["title"], key=key, value=sfsFreeShippingSum_value
                )
                assert configs_response.status_code == 204

        with allure.step("Получаем созданную корзину с суммой товаров = трешолду"):
            cart = self.api_cart.get(cart_uuid=cart_uuid)
            assert cart.json()["data"]["cartUuid"]

        with allure.step("Проверяем, leftToTreshold = 0"):
            assert cart.json()["data"]["order"]["leftToTreshold"] == 0

        with allure.step("Отправляем запрос на получение методов доставки"):
            delivery_methods_response = self.api_delivery.get_delivery_methods(cart_uuid=cart_uuid)
            assert delivery_methods_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки равна 0"):
            assert delivery_methods_response.json()["data"][0]["price"] == 0
            if (len(delivery_methods_response.json()["data"])>1):
                assert delivery_methods_response.json()["data"][1]["price"] == 0

        with allure.step("Отправляем запрос на получение списка пвз"):
            pickpoints_response = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickpoints_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем пвз равна 0"):
            count_pickpoints = helpers.count_value_key_in_list(
                iterable=pickpoints_response.json()["data"], key="deliveryPrice", value=0
            )
            assert len(pickpoints_response.json()["data"]) == count_pickpoints

        with allure.step("Отправляем запрос на получение списка интервалов"):
            address = utils.get_address()
            intervals_response = self.api_delivery.get_intervals(cart_uuid=cart_uuid, address=address["intervals"])
            assert intervals_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем интервалам равна 0"):
            assert intervals_response.json()["data"]["services"][0]["priceMin"] == 0
            assert intervals_response.json()["data"]["services"][1]["priceMin"] == 0

        with allure.step("Изменяем сумму трешхолда на +1"):
            with allure.step("Изменяем значение по ключу через апи"):
                sfsFreeShippingSum_value = sfsFreeShippingSum_value + 1
                configs_response = self.api_private_config.update_single(
                    title=config_bd[0]["title"], key=key, value=sfsFreeShippingSum_value
                )
                assert configs_response.status_code == 204

        with allure.step("Получаем созданную корзину с суммой товаров = трешолду +1"):
            cart = self.api_cart.get(cart_uuid=cart_uuid)
            assert cart.json()["data"]["cartUuid"]

        with allure.step("Проверяем, leftToTreshold = 1"):
            assert cart.json()["data"]["order"]["leftToTreshold"] == 1

        with allure.step("Отправляем запрос на получение методов доставки"):
            delivery_methods_response = self.api_delivery.get_delivery_methods(cart_uuid=cart_uuid)
            assert delivery_methods_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки больше 0"):
            omni2_enabled = self.entity_by_id(table="cities", id=2)["omni_2"]
            if omni2_enabled:
                assert delivery_methods_response.json()["data"][0]["price"] >= 0
                if len(delivery_methods_response.json()["data"]) > 1:
                    assert delivery_methods_response.json()["data"][1]["price"] > 0
            else:
                assert delivery_methods_response.json()["data"][0]["price"] > 0
                if len(delivery_methods_response.json()["data"]) > 1:
                    assert delivery_methods_response.json()["data"][1]["price"] > 0

        with allure.step("Отправляем запрос на получение списка пвз"):
            pickpoints_response = self.api_delivery.get_pickpoints(cart_uuid=cart_uuid, methods=["pickup"])
            assert pickpoints_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем пвз > 0"):
            count_pickpoints = helpers.count_value_key_in_list(
                iterable=pickpoints_response.json()["data"], key="deliveryPrice", value=0
            )
            assert count_pickpoints == 0

        with allure.step("Отправляем запрос на получение списка интервалов"):
            address = utils.get_address()
            intervals_response = self.api_delivery.get_intervals(cart_uuid=cart_uuid, address=address["intervals"])
            assert intervals_response.status_code == 200

        with allure.step("Проверяем, что сумма доставки по всем интервалам больше 0"):
            assert intervals_response.json()["data"]["services"][0]["priceMin"] > 0
            assert intervals_response.json()["data"]["services"][1]["priceMin"] > 0
