import allure
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders import utils
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.config.private import ConfigPrivate
from allure_commons.types import Severity

from befree.api_model.test_data.order import payment_common, payment_sbp


class TestDeliveryMethodsAvailability(OrdersPublic, QueriesCatalog, ConfigPrivate):
    @allure.id("2739")
    @allure.title("Доступность СБП для типов доставки для корзины с доставкой. Для SFS ПВЗ")
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяется для быстрой корзины с доставкой в ПВЗ. Ключ с методом оплаты в конфигах - sfsPaymentPickupPoint"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_methods_availability_pickup_sfs(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в сфс"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None)

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"], methods=["pickup"]
            )
            assert pickuppoints.status_code == 200

        with allure.step("Обновляем корзину с доставкой в ПВЗ"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_sfs_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_sfs_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_sfs_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки sfs ПВЗ"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_sfs_pickup_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_sfs_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_sfs_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_sfs_response.json()["data"]["delivery"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2741")
    @allure.title("Доступность СБП для типов доставки для корзины с доставкой. Для SFS курьером")
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяется для быстрой корзины с доставкой курьером. Ключ с методом оплаты в конфигах - "
        "sfsPaymentCourier"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_methods_availability_delivery_sfs(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в сфс"):
            variation = self.find_variation_by_availability_condition(qty_sfs="> 1", qty_ff=None)

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный интервал курьера"):
            address = utils.get_address()
            delivery_intervals = self.api_delivery.get_intervals(cart_uuid=cart_uuid, address=address["intervals"])
            assert delivery_intervals.status_code == 200

        with allure.step("Обновляем корзину с курьерской доставкой"):
            interval_id = delivery_intervals.json()["data"]["services"][0]["dates"][0]["intervals"][0]["id"]
            cart_with_shipping = self.api_cart.update_delivery(
                cart_uuid=cart_uuid, interval_id=interval_id, address=address["shipping"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_sfs_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_sfs_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_sfs_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки sfs курьером"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_sfs_delivery_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_sfs_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_sfs_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_sfs_response.json()["data"]["delivery"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2744")
    @allure.title("Доступность СБП для типов доставки для корзины с доставкой. Для ff ПВЗ")
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяется для обычной корзины с доставкой в ПВЗ. Ключ с методом оплаты в конфигах - "
        "paymentPickupPoint"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_methods_availability_pickup_ff(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в ff"):
            variation = self.find_variation_by_availability_condition(qty_ff="> 1", qty_sfs=None)

        with allure.step("Создаем  корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный ПВЗ"):
            pickuppoints = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"], methods=["pickup"]
            )
            assert pickuppoints.status_code == 200

        with allure.step("Обновляем корзину с доставкой в ПВЗ"):
            cart_with_shipping = self.api_cart.update_pickup(
                cart_uuid=cart_uuid, pickpoint_id=pickuppoints.json()["data"][0]["id"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки sfs ПВЗ"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_pickup_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2738")
    @allure.title("Доступность СБП для типов доставки для корзины с доставкой. Для ff курьером")
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяется для обычной корзины с доставкой курьером. Ключ с методом оплаты в конфигах - "
        "paymentCourier"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_methods_availability_delivery_ff(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в ff"):
            variation = self.find_variation_by_availability_condition(qty_ff="> 1", qty_sfs=None)

        with allure.step("Создаем  корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(items=items, current_tab="delivery")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный интервал курьера"):
            address = utils.get_address()
            delivery_intervals = self.api_delivery.get_intervals(cart_uuid=cart_uuid, address=address["intervals"])
            assert delivery_intervals.status_code == 200

        with allure.step("Обновляем корзину с курьерской доставкой"):
            interval_id = delivery_intervals.json()["data"]["services"][0]["dates"][0]["intervals"][0]["id"]
            cart_with_shipping = self.api_cart.update_delivery(
                cart_uuid=cart_uuid, interval_id=interval_id, address=address["shipping"]
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки ff курьером"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_delivery_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2740")
    @allure.title("Доступность СБП для типов доставки для корзины с доставкой. Для Омни1")
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяется для быстрой корзины с доставкой в омни1. Ключ с методом оплаты в конфигах - "
        "paymentOMNI"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_methods_availability_omni(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation = self.find_variation_by_availability_condition(qty_omni="> 1", city_id_in=2)

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="omni")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Ищем доступный магазин"):
            pickuppoints = self.api_delivery.get_pickpoints(
                cart_uuid=cart.json()["data"]["cartUuid"], methods=["reserveinstore"]
            )
            assert pickuppoints.status_code == 200

        with allure.step("Обновляем корзину с доставкой в магазин омни1"):
            cart_with_shipping = self.api_cart.update_reserveinstore(
                cart_uuid=cart_uuid,
                store_id=pickuppoints.json()["data"][0]["id"],
                store_external_id=pickuppoints.json()["data"][0]["id"],
            )
            assert cart_with_shipping.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_omni_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_omni_response.status_code == 200

        with allure.step("Проверяем, что для вкладки omni метод оплаты сбп доступен"):
            assert sbp_for_omni_response.json()["data"]["omni"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки омни1"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_omni_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_omni_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_omni_response.status_code == 200

        with allure.step("Проверяем, что для вкладки omni метод оплаты сбп недоступен"):
            assert sbp_for_omni_response.json()["data"]["omni"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2742")
    @allure.title("Доступность СБП для типов доставки для корзины без данных о доставке. Для омни")
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяем для вкладки омни"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_availability_without_shipping_omni(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в омни1"):
            variation = self.find_variation_by_availability_condition(qty_omni="> 1", city_id_in=2)

        with allure.step("Создаем быструю корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create_fast_cart(items=items, current_tab="omni")
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_omni_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_omni_response.status_code == 200

        with allure.step("Проверяем, что для вкладки omni метод оплаты сбп доступен"):
            assert sbp_for_omni_response.json()["data"]["omni"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки омни1"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_omni_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_omni_response = self.api_delivery.delivery_methods_availability(cart_uuid=cart_uuid)
            assert sbp_for_omni_response.status_code == 200

        with allure.step("Проверяем, что для вкладки omni метод оплаты сбп недоступен"):
            assert sbp_for_omni_response.json()["data"]["omni"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2745")
    @allure.title(
        "Доступность СБП для типов доставки для корзины без данных о доставке. Для деливери, омни2 в городе выключен"
    )
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяем для вкладки деливери на городе, где выключен омни2"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_availability_without_shipping_delivery_omni2_off(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в ff"):
            variation = self.find_variation_by_availability_condition(qty_ff="> 1", qty_sfs=None)

        with allure.step("Для доставки выбираем Собакино, чтобы не был включен омни2"):
            fias_id = "5438fbd9-c2f2-4f67-9607-9775c42df7cd"
            golden_record = "soba-098952"

        with allure.step("Создаем  корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(
                items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden_record
            )
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки ff ПВЗ"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_pickup_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Отключаем метод оплаты сбп для доставки ff курьером"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_delivery_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки ff ПВЗ и курьером"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_pickup_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

    @allure.id("2743")
    @allure.title(
        "Доступность СБП для типов доставки для корзины без данных о доставке. Для деливери, омни2 в городе включен"
    )
    @allure.description(
        "Метод возвращает доступные вкладки корзины (omni и delivery), по которым для методов доставок включен метод "
        "оплаты СБП. Проверяем для вкладки деливери на городе, где включен омни2"
    )
    @allure.tag("API Test")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Orders")
    @allure.label("feature", "MyCard")
    def test_delivery_availability_without_shipping_delivery_omni2_on(self):
        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Находим товар, который есть в наличии в ff"):
            variation = self.find_variation_by_availability_condition(qty_ff="> 1", qty_sfs=None)

        with allure.step("Для доставки выбираем город, где включен омни2"):
            conditions = ["omni_2 is true"]
            city = self.query_by_conditions(table="cities", conditions=conditions)
            fias_id = city[0]["fias_id"]
            golden_record = city[0]["golden_record"]

        with allure.step("Создаем  корзину с этим вариантом"):
            items = [{"id": variation[0]["variation_id"], "qty": 1}]
            cart = self.api_cart.create(
                items=items, current_tab="delivery", fias_id=fias_id, golden_record=golden_record
            )
            assert cart.json()["data"]["cartUuid"]
            cart_uuid = cart.json()["data"]["cartUuid"]

        with allure.step("Запрашиваем доступность сбп для корзины"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки ff ПВЗ"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_pickup_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп доступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Отключаем метод оплаты сбп для доставки ff курьером"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_delivery_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204

        with allure.step("Отключаем метод оплаты сбп для доставки омни2"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_omni2_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is True

        with allure.step("Отключаем метод оплаты сбп для доставки ff ПВЗ, курьером и омни2"):
            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_pickup_sbp_off)
            assert payment_settings.status_code == 204

            payment_settings = self.api_private_config.update(configs=payment_sbp.query_ff_delivery_sbp_off)
            assert payment_settings.status_code == 204

        with allure.step("Запрашиваем доступность сбп для корзины повторно"):
            sbp_for_ff_response = self.api_delivery.delivery_methods_availability(
                cart_uuid=cart_uuid, fias_id=fias_id, golden_record=golden_record
            )
            assert sbp_for_ff_response.status_code == 200

        with allure.step("Проверяем, что для вкладки delivery метод оплаты сбп недоступен"):
            assert sbp_for_ff_response.json()["data"]["delivery"] is False

        with allure.step("Включаем все методы оплат для всех типов доставок"):
            payment_settings = self.api_private_config.update(configs=payment_common.query_all_on)
            assert payment_settings.status_code == 204
