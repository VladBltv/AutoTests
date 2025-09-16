import allure
from allure_commons.types import Severity
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders.public import OrdersPublic
from utils import helpers


class TestRemoveFromCart(QueriesCatalog, OrdersPublic):
    @allure.title("Удаление товара из корзины: товар есть в обоих вкладках")
    @allure.label("microservice", "Public")
    @allure.feature("Yandex")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.description(
        """Проверяем, что в datalayer записываются два события удаления товара, если он находится в обоих вкладках"""
    )
    def test_remove_from_cart_both_tabs(self, shop_page) -> None:
        with allure.step("Найти товар, который есть в наличии и в омни и в фулфилменте"):
            variation_id = self.find_omniAndSf_stocks(city_id=6, store_id=1, qty=3)

        with allure.step("Добавить товар в корзину через api"):
            cart_create_response = self.api_cart.create(items=[{"id": variation_id, "qty": 1}])
            cart_uuid = cart_create_response.json()["data"]["cartUuid"]

        with allure.step("Перейти на сайт"):
            shop_page.goto("/zhenskaya")

        with allure.step("Установить uuid корзины в куки и в localStorage"):
            cart_cookies = helpers.cookies_for_shop(name="cartUuid", value=cart_uuid)
            shop_page.context.add_cookies([cart_cookies])
            shop_page.evaluate(f"localStorage.setItem('cartUuid', '{cart_uuid}')")

        with allure.step("Перейти на страницу корзины"):
            shop_page.goto("/cart")

        with allure.step("Очистить datalayer"):
            shop_page.evaluate(
                """() => {
                window.dataLayer = [];
            }"""
            )

        with allure.step("Удалить товар из из вкладки Доставка"):
            shop_page.get_by_test_id("minus").click()

        with allure.step("Проверить, что событие удаления товара записано в datalayer"):
            datalayer = shop_page.evaluate(
                """() => {
                return dataLayer.filter(item=>item['ecommerce']).filter(item => {return  ~JSON.stringify(item).indexOf('remove')}) || [];
            }"""
            )
            assert len(datalayer) == 0

        with allure.step("Очистить datalayer"):
            shop_page.evaluate(
                """() => {
                window.dataLayer = [];
            }"""
            )

        with allure.step("Удалить товар из из вкладки В Магазине"):
            shop_page.get_by_test_id("minus").click()

        with allure.step("Проверить, что событие удаления товара записано в datalayer"):
            datalayer = shop_page.evaluate(
                """() => {
                return dataLayer.filter(item=>item['ecommerce']).filter(item => {return  ~JSON.stringify(item).indexOf('remove')}) || [];
            }"""
            )
            assert len(datalayer) == 1
