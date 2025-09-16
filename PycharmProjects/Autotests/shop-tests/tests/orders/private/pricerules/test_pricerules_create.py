import allure

from befree.api_model.orders.private import OrdersPrivate
from befree.api_model.orders.db_queries.queries import QueriesOrders
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from allure_commons.types import Severity
from datetime import datetime, date, timedelta
from mimesis import Text, Generic
from pytest_check import check


class TestPricerulesCreate(OrdersPrivate, QueriesOrders, QueriesCatalog):
    @allure.id("2330")
    @allure.title("Создание прайсрула: валидация поля title")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, что нельзя создать прайсрул без поля title""")
    def test_create_pricerule_title_validate(self):
        with allure.step("Создаем прайсрул без title"):
            title = None
            create_pricerule_response = self.api_pricerules.create(title=title)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с пустым полем title"):
            title = ""
            create_pricerule_response = self.api_pricerules.create(title=title)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с полем title, у которого количество символов больше 256 символов"):
            title = Text("ru").text()[:257]
            create_pricerule_response = self.api_pricerules.create(title=title)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с заполненным полем title"):
            title = Text("ru").title()[:100]
            create_pricerule_response = self.api_pricerules.create(title=title)

        with allure.step("Проверяем, что прайсрул  создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

    @allure.id("2338")
    @allure.title("Создание прайсрула: валидация поля type_id")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, что нельзя создать прайсрул без поля type_id""")
    def test_create_pricerule_type_validate(self):
        with allure.step("Создаем прайсрул без type_id"):
            type_id = None
            create_pricerule_response = self.api_pricerules.create(typeId=type_id)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с несуществующим type_id"):
            type_id = 0
            create_pricerule_response = self.api_pricerules.create(typeId=type_id)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'промокод' без данных промокода"):
            type_id = 1
            create_pricerule_response = self.api_pricerules.create(typeId=type_id, promocodes=None)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'промокод' c данными промокода"):
            type_id = 1
            promocodes = {
                "counterType": "perUser",
                "counterAmount": 1,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(typeId=type_id, promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с типом 'способ оплаты' без условия на способ оплаты"):
            type_id = 2
            create_pricerule_response = self.api_pricerules.create(typeId=type_id, conditions=None)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'способ оплаты' с условием на способ оплаты"):
            type_id = 2
            conditions = [
                {
                    "type": "paymentMethod",
                    "operand": "in",
                    "condition": ["podeli"]
                }
            ]
            create_pricerule_response = self.api_pricerules.create(typeId=type_id, conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

    @allure.id("2340")
    @allure.title("Создание прайсрула: валидация поля discounts")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, что нельзя создать прайсрул без поля discounts""")
    def test_create_pricerule_discounts_validate(self):
        with allure.step("Создаем прайсрул без discounts"):
            discounts = None
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с некорректным типом discounts"):
            discounts = {
                "type": "qwe",
                "amount": 30,
                "deliveryPercent": 0
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'в рублях' и значением = 0"):
            discounts = {
                "type": "sum",
                "amount": 0,
                "deliveryPercent": 0
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'в рублях' и значением > 0 и платной доставкой"):
            discounts = {
                "type": "sum",
                "amount": 300,
                "deliveryPercent": 0
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с типом 'в процентах' и значением = 0"):
            discounts = {
                "type": "percent",
                "amount": 0,
                "deliveryPercent": 0
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'в процентах' и значением = 100"):
            discounts = {
                "type": "percent",
                "amount": 100,
                "deliveryPercent": 0
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с типом 'в процентах' и значением от 1 до 99 и бесплатной доставкой"):
            discounts = {
                "type": "percent",
                "amount": 30,
                "deliveryPercent": 100
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул  создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с бесплатной доставкой, без скидок"):
            discounts = {
                "deliveryPercent": 100
            }
            create_pricerule_response = self.api_pricerules.create(discounts=discounts)

        with allure.step("Проверяем, что прайсрул  создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

    @allure.id("2333")
    @allure.title("Создание прайсрула: валидация поля promocodes")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, что нельзя создать прайсрул без поля promocodes""")
    def test_create_pricerule_promocodes_validate(self):
        with allure.step("Создаем прайсрул без promocodes"):
            promocodes = None
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            check.equal(create_pricerule_response.status_code, 422, "Status code should be 422")

        with allure.step("Создаем прайсрул с некорректным типом promocodes"):
            promocodes = {
                "counterType": "qwe",
                "counterAmount": 1,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с количеством применений = 0"):
            promocodes = {
                "counterType": "general",
                "counterAmount": 0,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с одноразовым промокодом"):
            promocodes = {
                "counterType": "general",
                "counterAmount": 1,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с многоразовым промокодом без ограничений"):
            promocodes = {
                "counterType": "general",
                "counterAmount": None,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с многоразовым промокодом с ограничением"):
            promocodes = {
                "counterType": "general",
                "counterAmount": 100,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с промокодом на пользователя с количеством = 0"):
            promocodes = {
                "counterType": "perUser",
                "counterAmount": 0,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с промокодом на пользователя с количеством > 0"):
            promocodes = {
                "counterType": "perUser",
                "counterAmount": 10,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }
            create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("При передаче в поле промокодов повторяющихся значений сохраняются только уникальные, повторы игнорируются"):
            with allure.step("Создать прайсрул с повторяющимся значением промокода"):
                promocode_value = Text("en").word() + str(Generic().random.randint(1, 100))
                promocodes = {
                    "counterType": "perUser",
                    "counterAmount": 10,
                    "values": [promocode_value, promocode_value]
                }
                create_pricerule_response = self.api_pricerules.create(promocodes=promocodes)

            with allure.step("Проверяем, что прайсрул создался, ответ 201, к прайсрулу привязан только один уникальный промокод"):
                check.equal(create_pricerule_response.status_code, 201, "Status code should be 201")
                check.equal(create_pricerule_response.json()["data"]["promocodes"]["values"][0], promocode_value, "Existing promocode value matches saved value")
                check.equal(len(create_pricerule_response.json()["data"]["promocodes"]["values"]), 1, "Promocodes length should be 1")


    @allure.id("2339")
    @allure.title("Создание прайсрула: валидация поля conditions")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, что нельзя создать прайсрул без поля conditions""")
    def test_create_pricerule_conditions_validate(self):
        with allure.step("Создаем прайсрул без conditions"):
            conditions = None
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        # with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
        #     assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с некорректным типом conditions"):
            conditions = [{
                "type": "qwe",
                "operand": ">",
                "condition": 3000
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул на сумму корзины с некорректным типом условия"):
            conditions = [{
                "type": "cartSum",
                "operand": "in",
                "condition": [3000]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул на сумму корзины"):
            conditions = [{
                "type": "cartSum",
                "operand": ">",
                "condition": 3000
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул на методы оплаты с некорректным ключом оплаты"):
            conditions = [{
                "type": "paymentMethod",
                "operand": "in",
                "condition": ['cash1']
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул на методы оплаты с пустым массивом оплат"):
            conditions = [{
                "type": "paymentMethod",
                "operand": "in",
                "condition": []
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201 и в ответе нет условия на метод оплаты"):
            assert create_pricerule_response.status_code == 201
            assert create_pricerule_response.json()["data"]["conditions"] == []


        with allure.step("Создаем прайсрул на методы оплаты"):
            conditions = [
                {
                    "type": "paymentMethod",
                    "operand": "in",
                    "condition": ["cash", "sber", "sbp", "podeli"],
                }
            ]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул на список товаров"):
            conditions = [{
                "type": "articles",
                "operand": "in",
                "condition": ['Wide9']
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул, который не применим к списку товаров"):
            conditions = [{
                "type": "articles",
                "operand": "notIn",
                "condition": ['Wide9']
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Создаем прайсрул на большой список товаров: 2000 артикулов"):
            products_from_db = self.get_product_articles(limit=5000)
            articles = [item['article'] for item in products_from_db]

            conditions = [{
                "type": "articles",
                "operand": "in",
                "condition": articles
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201 и в ответе есть ограничение на артикулы"):
            assert create_pricerule_response.status_code == 201
            assert create_pricerule_response.json()["data"]["conditions"][0]["condition"] != []


        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с отбором по подборке"):
            cond = ["is_category = false and parent_id is null"]
            compilation_id, slug, gender = self.get_compilation_by_conditions(conditions=cond)
            conditions = [{
                "type": "compilations",
                "operand": "in",
                "condition": [int(compilation_id)]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с отбором по категории"):
            cond = ["is_category = true"]
            category_id, slug, gender = self.get_compilation_by_conditions(conditions=cond)
            conditions = [{"type": "compilations", "operand": "in", "condition": [int(category_id)]}]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с отбором по стикеру new"):
            conditions = [{
                "type": "stickers",
                "operand": "in",
                "condition": ["new"]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с отбором по стикеру не sale"):
            conditions = [{
                "type": "stickers",
                "operand": "notIn",
                "condition": ["sale"]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с несуществующей платформой"):
            conditions = [{
                "type": "platform",
                "operand": "in",
                "condition": ["qwe"]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с платформой app"):
            conditions = [{
                "type": "platform",
                "operand": "in",
                "condition": ["app"]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с платформой app и web"):
            conditions = [{
                "type": "platform",
                "operand": "in",
                "condition": ["app", "web"]
            }]
            create_pricerule_response = self.api_pricerules.create(conditions=conditions)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

    @allure.id("2334")
    @allure.title("Создание прайсрула: валидация поля dates")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем валидацию полей с датами""")
    def test_create_pricerule_dates_validate(self):
        with allure.step("Создаем прайсрул без dateStart и dateEnd"):
            dateStart = None
            dateEnd = None
            create_pricerule_response = self.api_pricerules.create(dateStart=dateStart, dateEnd=dateEnd)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул: dateStart=null и dateEnd=дата"):
            dateStart = None
            dateEnd = datetime.today().strftime('%Y-%m-%d')
            create_pricerule_response = self.api_pricerules.create(dateStart=dateStart, dateEnd=dateEnd)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул: dateStart=дата и dateEnd=нулл"):
            dateStart = datetime.today().strftime('%Y-%m-%d')
            dateEnd = None
            create_pricerule_response = self.api_pricerules.create(dateStart=dateStart, dateEnd=dateEnd)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул: dateStart=дата и dateEnd=дата"):
            dateStart = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            dateEnd = datetime.today().strftime('%Y-%m-%d')
            create_pricerule_response = self.api_pricerules.create(dateStart=dateStart, dateEnd=dateEnd)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул: dateStart > dateEnd"):
            dateStart = datetime.today().strftime('%Y-%m-%d')
            dateEnd = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            create_pricerule_response = self.api_pricerules.create(dateStart=dateStart, dateEnd=dateEnd)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

    # нельзя создать прайсрул с промокодом, который сейчас активен
    @allure.id("2328")
    @allure.title("Создание прайсрула: валидация значения промокода")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Нельзя создать прайсрул с промокодом, который  активен в другом прайсруле на этот период""")
    def test_value_promocode(self):
        with allure.step("Создаем прайсрул с промокодом, действующий в определенный период"):
            promocode_value = Text("en").word() + str(Generic().random.randint(1, 100))
            promocodes = {
                "counterType": "general",
                "counterAmount": 1,
                "values": [promocode_value]
            }
            dateStart = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
            dateEnd = datetime.today().strftime('%Y-%m-%d')

            create_pricerule_response = self.api_pricerules.create(
                dateStart=dateStart,
                dateEnd=dateEnd,
                promocodes=promocodes
            )

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

        with allure.step("Создаем прайсрул с этим же промокодом, действующий в этот же период"):
            dateStart = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
            dateEnd = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            create_pricerule_response = self.api_pricerules.create(
                dateStart=dateStart,
                dateEnd=dateEnd,
                promocodes=promocodes
            )

        with allure.step("Проверяем, что в ответе 200 и сообщение об ошибке Один из промокодов уже используется в выбранном периоде"):
            assert create_pricerule_response.status_code == 200
            assert create_pricerule_response.json()[ "alerts"][0]["title"] == "Повторяющийся промокод"
            assert create_pricerule_response.json()["alerts"][0]["text"] == "Один из промокодов уже используется в выбранном периоде"
            assert create_pricerule_response.json()["alerts"][0]["type"] == "ERROR"

        with allure.step("Создаем прайсрул с этим же промокодом, действующий в другой период"):
            dateStart = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
            dateEnd = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
            create_pricerule_response = self.api_pricerules.create(
                dateStart=dateStart,
                dateEnd=dateEnd,
                promocodes=promocodes
            )

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201

    @allure.id("2812")
    @allure.title("Создание прайсрула: валидация поля productsListType")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем валидацию полей с датами""")
    def test_create_pricerule_products_list_type_validate(self):
        with allure.step("Создаем прайсрул без productsListType"):
            products_list_type = None
            create_pricerule_response = self.api_pricerules.create(productsListType=products_list_type)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул с пустым полем productsListType"):
            products_list_type = ""
            create_pricerule_response = self.api_pricerules.create(productsListType=products_list_type)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул со значением поля productsListType не из списка допустимых"):
            products_list_type = "qwerty"
            create_pricerule_response = self.api_pricerules.create(productsListType=products_list_type)

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert create_pricerule_response.status_code == 422

        with allure.step("Создаем прайсрул со значением поля productsListType = all"):
            products_list_type = "all"
            create_pricerule_response = self.api_pricerules.create(productsListType=products_list_type)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201
            assert create_pricerule_response.json()["data"]["productsListType"] == products_list_type

        with allure.step("Создаем прайсрул со значением поля productsListType = compilations"):
            products_list_type = "compilations"
            create_pricerule_response = self.api_pricerules.create(productsListType=products_list_type)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201
            assert create_pricerule_response.json()["data"]["productsListType"] == products_list_type

        with allure.step("Создаем прайсрул со значением поля productsListType = articles"):
            products_list_type = "articles"
            create_pricerule_response = self.api_pricerules.create(productsListType=products_list_type)

        with allure.step("Проверяем, что прайсрул создался, ответ 201"):
            assert create_pricerule_response.status_code == 201
            assert create_pricerule_response.json()["data"]["productsListType"] == products_list_type

