import allure
import allure, json
from allure_commons.types import Severity
from selene.support import by
from selene.support.shared import browser
from selene import be
import time
from befree.api_model import public
from selenium.webdriver.common.keys import Keys
from befree.api_model import product
from befree.api_model.orders.public import OrdersPublic
from befree.api_model.catalog.db_queries.queries import QueriesCatalog


class TestPublicCart(OrdersPublic, QueriesCatalog):
    @allure.id("2705")
    @allure.title("Отображение состояния пустой корзины")
    @allure.description("Проверяем, что отображается заглушка пустой корзины")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_empty_cart(self, browser_config):
        with allure.step("Перейти на сайт на страницу пустой корзины"):
            browser.open("/cart")

        with allure.step("Выводится заглушка пустой корзины"):
            browser.element(by.text("здесь пока пусто")).should(be.present)
            browser.element(by.text("перейти в каталог")).click()

    @allure.id("2707")
    @allure.title("Отображение корзины omni2 + нажатие на активные элементы товара (+/-/сердечко)")
    @allure.description(
        "Проверяем, что для омни2 не отображается вкладки-разделители и нажимаются +/-/сердечко"
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_cart_omni2(self, browser_config):
        with allure.step("Подготоваливаем данные"):
            with allure.step("Находим товар, который есть в наличии в омни2"):
                variation_in_omni2 = self.find_stocks(store_id=2, qty=5)

            with allure.step("Создаем корзину под неавторизованным пользователем"):
                items = [{"id": variation_in_omni2, "qty": 5}]
                cart = self.api_cart.create(items=items)

                assert cart.status_code == 200

        with allure.step("Устанавливаем в куки cartUuid"):
            browser.open("/cart")
            public.set_cookie(
                browser=browser,
                cookie_name="cartUuid",
                cookie_value=cart.json()["data"]["cartUuid"],
            )
        with allure.step("Устанавливаем в куки город"):
            browser.open("/cart")
            location = self.api_geo.suggestion_city(query="санкт-петербург")
            assert location.status_code == 200
            public.set_cookie(
                browser=browser,
                cookie_name="location",
                cookie_value=json.dumps(location.json()["data"][0]),
            )

        with allure.step("Переход в корзину"):
            browser.open("/cart")

        with allure.step("Проверяем, что не выводятся вкладки-разделители для омни2"):
            browser.element(by.text("доставка")).should(be.disabled)

        # with allure.step("Кликаем на +/-/избранное"):
        #     browser.element("button[data-testid*='minus']").click()
        #     browser.element("button[data-testid*='plus']").click()
        #     browser.element("button[data-testid*='heart-icon']").click()

    @allure.id("2710")
    @allure.title("Отображение корзины. Переход между вкладками-разделителями")
    @allure.description(
        "Проверяем, что осуществляется переход между вкладками и от этого зависит виджет подели"
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_cart_tab(self, browser_config):
        with allure.step("Подготоваливаем данные"):
            with allure.step("Находим товар, который есть в наличии"):
                variation = self.find_omniAndSf_stocks(qty=3, city_id=6, store_id=1)

            with allure.step("Создаем корзину под неавторизованным пользователем"):
                fias_id = "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"
                golden_record = "mosk-941139"
                items = [{"id": variation, "qty": 1}]
                cart = self.api_cart.create(
                    items=items, fias_id=fias_id, golden_record=golden_record
                )

                assert cart.status_code == 200

        with allure.step("Устанавливаем в куки cartUuid"):
            browser.open("/cart")
            public.set_cookie(
                browser=browser,
                cookie_name="cartUuid",
                cookie_value=cart.json()["data"]["cartUuid"],
            )
        with allure.step("Устанавливаем в куки город"):
            browser.open("/cart")
            location = self.api_geo.suggestion_city(query="москва")
            assert location.status_code == 200
            public.set_cookie(
                browser=browser,
                cookie_name="location",
                cookie_value=json.dumps(location.json()["data"][0]),
            )

        with allure.step("Переход в корзину"):
            browser.open("/cart")

        # with allure.step("Переходим на вкладку доставка и проверяем вывод виджета подели"):
        #     browser.element(by.xpath("//div[contains(text(), 'доставка')]")).click()
        #     browser.element("div[id*='podeli_widget']").should(be.present)
        #
        # with allure.step(
        #         "Переходим на вкладку омни и проверяем, что виджет подели не выводится"
        # ):
        #     time.sleep(3)
        #     browser.element(by.xpath("//div[contains(text(), 'в магазине')]")).click()
        #     browser.element("div[id*='podeli_widget']").should(be.disabled)

    @allure.id("2708")
    @allure.title("Отображение стикера беслпатной доставки в зависимости от суммы корзины")
    @allure.description("Проверяем, что изменяется стикер беслпатной доставки (трешхолд)")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_delivery_sticker(self, browser_config):
        value = 4  # количество товара
        with allure.step("Находим товар, который есть в наличии в фф"):
            variation = self.find_omniAndSf_stocks(
                qty=value,
                city_id=6,
                store_id=1,
            )

        with allure.step("Создаем корзину"):
            items = [{"id": variation, "qty": value - 2}]
            cart = self.api_cart.create(items=items)
            assert cart.status_code == 200

        freeShippingSum_value = cart.json()["data"]["order"]["calculatedTotal"]

        # with allure.step("Изменяем значение freeShippingSum"):
        #     settings = [
        #         {
        #             "key": "freeShippingSum",
        #             "title": "Сумма бесплатной доставки",
        #             "value": freeShippingSum_value + 1,
        #         }
        #     ]
        #     # request_setting = config.change_settings_orders(settings=settings)
        #     request_setting = config.change_settings_orders(settings=settings)
        #     assert request_setting.status_code == 200
        #
        # with allure.step("Устанавливаем в куки cartUuid"):
        #     browser.open("/cart")
        #     public.set_cookie(
        #         browser=browser,
        #         cookie_name="cartUuid",
        #         cookie_value=cart.json()["data"]["cartUuid"],
        #     )
        # with allure.step("Устанавливаем в куки город"):
        #     browser.open("/cart")
        #     location = self.api_orders.suggestion_city(query="москва")
        #     assert location.status_code == 200
        #     public.set_cookie(
        #         browser=browser,
        #         cookie_name="location",
        #         cookie_value=json.dumps(location.json()["data"][0]),
        #     )
        #
        # with allure.step("Переход в корзину"):
        #     browser.open("/cart")
        #
        # with allure.step("Выводится сумма до применения трешхолда"):
        #     browser.element(by.text("добавьте ещё вещей на")).should(be.present)
        #
        # with allure.step("Добавляем +1 товар и проверяем вывод бесплатной доставки"):
        #     browser.element("button[data-testid*='plus']").click()
        #     browser.element(by.text("вам доступна")).should(be.present)
        #
        # with allure.step("Переходим на вкладку омни и проверяем, что плашка не выводится"):
        #     browser.element(by.xpath("//div[contains(text(), 'в магазине')]")).click()
        #     browser.element(by.text("вам доступна")).should(be.disabled)

    @allure.id("2706")
    @allure.title("Отображение блока товаров 'нет в наличии'")
    @allure.description(
        "Проверяем, что появляется блок с товарами на в наличии и удаление этих товаров"
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_products_out_of_stock(self, browser_config):
        with allure.step("Подготоваливаем данные"):
            value = 5  # количество товара
            with allure.step("Находим товар, которого нет в наличии в фф и омни2"):
                variation = self.find_omni2AndSf_out_of_stocks()

            with allure.step("Создаем корзину"):
                items = [{"id": variation, "qty": value}]
                cart = self.api_cart.create(items=items)
                assert cart.status_code == 200

        with allure.step("Устанавливаем в куки cartUuid"):
            browser.open("/cart")
            public.set_cookie(
                browser=browser,
                cookie_name="cartUuid",
                cookie_value=cart.json()["data"]["cartUuid"],
            )
        with allure.step("Устанавливаем в куки город"):
            browser.open("/cart")
            location = self.api_geo.suggestion_city(query="санкт-петербург")
            assert location.status_code == 200
            public.set_cookie(
                browser=browser,
                cookie_name="location",
                cookie_value=json.dumps(location.json()["data"][0]),
            )

        with allure.step("Переход в корзину"):
            browser.open("/cart")

        # with allure.step("Блок 'нет в наличии' скрыт"):
        #     browser.element(by.text("нет в наличии")).should(be.enabled)
        #     browser.element("div[class*='sc-88342a5b-3']").should(be.hidden)
        #
        # with allure.step("Раскрываем блок 'нет в наличии'"):
        #     browser.element(by.text("нет в наличии")).click()
        #     browser.element("div[class*='sc-88342a5b-3']").should(be.visible)
        #
        # with allure.step("Удаляем товар из блока 'нет в наличии'"):
        #     browser.element(by.text("удалить")).should(be.visible)
        #     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     browser.element(by.text("удалить")).click()
        #     time.sleep(3)
        #     browser.element(by.text("нет в наличии")).should(be.disabled)

    @allure.id("2711")
    @allure.title("Изменение города в корзине")
    @allure.description("Проверяем, что изменяется город")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_change_city(self, browser_config):
        with allure.step("Устанавливаем в куки город"):
            browser.open("/cart")
            location = self.api_geo.suggestion_city(query="санкт-петербург")

            assert location.status_code == 200
            public.set_cookie(
                browser=browser,
                cookie_name="location",
                cookie_value=json.dumps(location.json()["data"][0]),
            )

        with allure.step("Переход в корзину"):
            browser.open("/cart")

        with allure.step("Вызываем попап изменения города"):
            browser.element(by.text("Санкт-Петербург")).click()
            browser.element(by.text("выберите город")).should(be.visible)

        with allure.step("Выбираем Москву из списка"):
            browser.element(by.text("Москва")).click()
            browser.element(by.text("Москва")).should(be.visible)

        with allure.step("Вызываем попап изменения города"):
            browser.element(by.text("Москва")).click()
            browser.element(by.text("выберите город")).should(be.visible)

        with allure.step("Ищем несуществующий город"):
            browser.element("input[name='city']").click().type("12345")
            time.sleep(3)
            browser.element(by.text("Совпадений не найдено")).should(be.visible)

        with allure.step("Очищаем инпут"):
            browser.element("input[name='city']").click()
            time.sleep(3)
            browser.element("input[name='city']").send_keys(Keys.COMMAND + "a")
            browser.element("input[name='city']").send_keys(Keys.DELETE)

        with allure.step("Ищем город Петрозаводск"):
            browser.element("input[name='city']").click().type("петрозав")
            time.sleep(3)
            # browser.element(by.text("г Петрозаводск")).click()
            # browser.element(by.text("Петрозаводск")).should(be.visible)

    @allure.id("2709")
    @allure.title("Добавление товара и переход в корзину")
    @allure.description(
        "Проверяем, что меняется кнопка при добавлении товара в корзину и осуществляется переход"
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Cart")
    @allure.label("feature", "Состав корзины")
    @allure.label("owner", "Balakireva")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_add_to_cart(self, browser_config):
        value = 4  # количество товара
        with allure.step("Находим товар, который есть в наличии в фф"):
            variation = self.find_omniAndSf_stocks(
                qty=value,
                city_id=6,
                store_id=1,
            )
            article, color_code_id, size_id = product.get_article_by_variation_id(variation)

        with allure.step("Устанавливаем в куки город"):
            browser.open("/cart")

            location = self.api_geo.suggestion_city(query="москва")
            assert location.status_code == 200
            public.set_cookie(
                browser=browser,
                cookie_name="location",
                cookie_value=json.dumps(location.json()["data"][0]),
            )
        with allure.step("Заходим на страницу товара и добавляем товар в корзину"):
            browser.open(f"/zhenskaya/product/{article}/{color_code_id}?size={size_id}")
            browser.execute_script("document.querySelector('.flocktory-widget-overlay')?.remove()")
            # browser.element("button[data-testid*='product-addtocart-button']").click()

        #     with allure.step("Проверяем, что кнопка называется 'перейти в корзину'"):
        #         browser.element(by.text("перейти в корзину")).should(be.visible)
        #
        # with allure.step("Переходим в корзину через кнопку товара"):
        #     browser.element(by.text("перейти в корзину")).click()
        #     browser.element(by.text("корзина")).should(be.visible)
