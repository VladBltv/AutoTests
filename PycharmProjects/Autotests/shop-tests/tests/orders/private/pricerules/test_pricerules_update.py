from datetime import datetime, timedelta
from pytest_check import check
import allure
from mimesis import Text, Generic
from befree.api_model.orders.private import OrdersPrivate
from befree.api_model.orders.db_queries.queries import QueriesOrders
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.orders import utils
from allure_commons.types import Severity
from datetime import datetime, date, timedelta


class TestPricerulesUpdate(OrdersPrivate, QueriesOrders, QueriesCatalog):
    @allure.id("2337")
    @allure.title("Изменение прайсрула со статусом pending")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, в прайсруле со статусом pending можно изменить все поля""")
    def test_update_pricerule_pending(self):
        with allure.step("Создаем прайсрул со статусом 'pending'"):
            date_start = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')
            create_pricerule_response = self.api_pricerules.create(dateStart=date_start)
            assert create_pricerule_response.status_code == 201
            pricerule_id = create_pricerule_response.json()["data"]["id"]

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Проверяем, что нет запрета изменений"):
            assert pricerule_response.json()["data"]["canEditAllData"] == True

    @allure.id("2336")
    @allure.title("Изменение прайсрула со статусом running")
    @allure.label("Service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, в прайсруле со статусом running можно изменить только дату окончания и описание""")
    def test_update_pricerule_running(self):
        with allure.step("Находим прайсрул со статусом 'running'"):
            pricerule_id = utils.get_pricerule_by_status(status="running")

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Проверяем, что есть запрет изменений"):
            assert pricerule_response.json()["data"]["canEditAllData"] == False

        with allure.step("Изменяем значения поля описания и даты окончания"):
            date_end = (datetime.today() + timedelta(1)).strftime("%Y-%m-%d")
            description = "description"

            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                description=description,
                dateEnd=date_end,
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что данные изменились"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

            assert pricerule_response.json()["data"]["description"] == description

        with allure.step("Изменяем другие поля"):
            title = "title"
            discounts = {
                "type": "percent" if pricerule_response.json()["data"]["discounts"]["type"] == "sum" else "sum",
                "amount": 30,
                "deliveryPercent": 100,
            }
            products_list_type = "articles" if pricerule_response.json()["data"]["productsListType"] == "all" else "compilations"
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                title=title,
                discounts=discounts,
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что данные не изменились"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

            assert pricerule_response.json()["data"]["title"] != title
            assert pricerule_response.json()["data"]["discounts"] != discounts

    @allure.id("2342")
    @allure.title("Изменение прайсрула со статусом ended")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Проверяем, в прайсруле со статусом ended можно изменить только дату окончания и описание""")
    def test_update_pricerule_ended(self):
        with allure.step("Находим прайсрул со статусом 'ended'"):
            pricerule_id = utils.get_pricerule_by_status(status="ended")

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Проверяем, что есть запрет изменений"):
            assert pricerule_response.json()["data"]["canEditAllData"] == False

        with allure.step("Изменяем значения поля описания и даты окончания"):
            date_from_response = pricerule_response.json()["data"]["dateEnd"]
            date_end = (datetime.strptime(date_from_response, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).strftime(
                "%Y-%m-%d")
            description = "description"

            update_response = self.api_pricerules.update(
                current_data=pricerule_response.json()["data"],
                pricerule_id=pricerule_id,
                dateEnd=date_end,
                description=description,
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что данные изменились"):
            assert update_response.json()["data"]["description"] == description

        with allure.step("Изменяем другие поля"):
            title = "title"
            discounts = {
                "type": "percent" if pricerule_response.json()["data"]["discounts"]["type"] == "sum" else "sum",
                "amount": 30,
                "deliveryPercent": 100,
            }
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                title=title,
                discounts=discounts,
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что данные не изменились"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

            assert pricerule_response.json()["data"]["title"] != title
            assert pricerule_response.json()["data"]["discounts"] != discounts

    @allure.id("2332")
    @allure.title("Обновление прайсрула: валидация поля title")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, прайсрул со статусом pending нельзя обновить без поля title""")
    def test_update_pricerule_title_validate(self):
        with allure.step("Находим прайсрул со статусом 'pending'"):
            pricerule_id = utils.get_pricerule_by_status(status="pending")

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем прайсрул без поля title"):
            title = None

            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                title=title,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )

        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с пустым полем title"):
            title = ""
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                title=title,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )

        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с полем title, у которого количество символов больше 256 символов"):
            title = Text("ru").text()[:257]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                title=title,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )

        with allure.step("Проверяем, что прайсрул не создался, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с заполненным полем title"):
            title = Text("ru").title()[:50]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                title=title,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
            )

        with allure.step("Проверяем, что прайсрул  обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["title"] == title

    @allure.id("2335")
    @allure.title("Обновление прайсрула: валидация поля type")
    @allure.label("Service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, прайсрул со статусом pending нельзя обновить без поля type""")
    def test_update_pricerule_type_validate(self):
        with allure.step("Находим прайсрул со статусом 'pending'"):
            pricerule_id = utils.get_pricerule_by_status(status="pending")

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем прайсрул без поля type_id"):
            type_id = None
            update_response = self.api_pricerules.update(pricerule_id=pricerule_id,
                                                         current_data=pricerule_response.json()["data"], typeId=type_id)

        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с несуществующим type_id"):
            type_id = 0
            update_response = self.api_pricerules.update(pricerule_id=pricerule_id,
                                                         current_data=pricerule_response.json()["data"], typeId=type_id)

        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем у прайсрула type_id"):
            type_id = 1 if pricerule_response.json()["data"]["type"]["id"] == 2 else 2
            update_response = self.api_pricerules.update(pricerule_id=pricerule_id,
                                                         current_data=pricerule_response.json()["data"], typeId=type_id)

        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["type"]["id"] == type_id

    @allure.id("2341")
    @allure.title("Обновление прайсрула: валидация поля discounts")
    @allure.label("Service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, прайсрул со статусом pending нельзя обновить без поля discounts""")
    def test_update_pricerule_discounts_validate(self):
        with allure.step("Находим прайсрул со статусом 'pending'"):
            pricerule_id = utils.get_pricerule_by_status(status="pending")

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем прайсрул без поля discounts"):
            discounts = None
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с некорректным типом discounts"):
            discounts = {"type": "qwe", "amount": 30, "deliveryPercent": 0}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с типом 'в процентах' и значением = 0"):
            discounts = {"type": "percent", "amount": 0, "deliveryPercent": 0}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с типом 'в рублях' и значением = 0"):
            discounts = {"type": "sum", "amount": 0, "deliveryPercent": 0}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с типом 'в процентах' и значением от 1 до 100 и платной доставкой"):
            discounts = {"type": "percent", "amount": 31, "deliveryPercent": 0}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["discounts"] == discounts

        with allure.step("Обновляем прайсрул с типом 'в рублях' и значением > 0 и бесплатной доставкой"):
            discounts = {"type": "sum", "amount": 301, "deliveryPercent": 100}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["discounts"] == discounts

        with allure.step("Обновляем прайсрул с бесплатной доставкой, без скидок"):
            discounts = {"deliveryPercent": 100}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                discounts=discounts,
            )
        with allure.step("Проверяем, что прайсрул  обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["discounts"]["type"] == None
            assert update_response.json()["data"]["discounts"]["amount"] == None
            assert update_response.json()["data"]["discounts"]["deliveryPercent"] == 100

    @allure.id("2331")
    @allure.title("Обновление прайсрула: валидация поля promocodes")
    @allure.label("Service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, прайсрул с типом промокод со статусом pending нельзя обновить без поля 
    promocodes""")
    def test_update_pricerule_promocodes_validate(self):
        with allure.step("Создаем прайсрул со статусом 'pending' и типом прайсрула промокод"):
            date_start = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')
            promocodes = {
                "counterType": "general",
                "counterAmount": 1,
                "values": [Text("en").word() + str(Generic().random.randint(1, 100))]
            }

            create_pricerule_response = self.api_pricerules.create(dateStart=date_start, promocodes=promocodes)
            assert create_pricerule_response.status_code == 201

            pricerule_id = create_pricerule_response.json()["data"]["id"]

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем прайсрул  без promocodes"):
            promocodes = None
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с некорректным значением поля counterType для промокода"):
            promocodes = {"counterType": "qwe", "counterAmount": 1,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с количеством применений = 0"):
            promocodes = {"counterType": "general", "counterAmount": 0,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с одноразовым промокодом"):
            promocodes = {"counterType": "general", "counterAmount": 1,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["promocodes"] == promocodes

        with allure.step("Обновляем прайсрул с многоразовым промокодом без ограничений"):
            promocodes = {"counterType": "general", "counterAmount": None,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["promocodes"] == promocodes

        with allure.step("Обновляем прайсрул с многоразовым промокодом с ограничением"):
            promocodes = {"counterType": "general", "counterAmount": 100,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["promocodes"] == promocodes

        with allure.step("Обновляем прайсрул с промокодом на пользователя с количеством = 0"):
            promocodes = {"counterType": "perUser", "counterAmount": 0,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с промокодом на пользователя с количеством > 0"):
            promocodes = {"counterType": "perUser", "counterAmount": 10,
                          "values": [Text("en").word() + str(Generic().random.randint(1, 100))]}
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                promocodes=promocodes,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["promocodes"] == promocodes


        with allure.step("При передаче в поле промокодов повторяющихся значений сохраняются только уникальные, повторы игнорируются"):
            with allure.step("Обновит прайсрул с повторяющимся значением промокода"):
                get_response = self.api_pricerules.get(pricerule_id=pricerule_id)
                promocodes_length = len(get_response.json()["data"]["promocodes"]["values"])

                promocode_value = Text("en").word() + str(Generic().random.randint(1, 100))
                promocodes = {
                    "counterType": "perUser",
                    "counterAmount": 10,
                    "values": get_response.json()["data"]["promocodes"]["values"] + [promocode_value, promocode_value]
                }

                update_response = self.api_pricerules.update(
                    pricerule_id=pricerule_id,
                    current_data=pricerule_response.json()["data"],
                    typeId=pricerule_response.json()["data"]["type"]["id"],
                    promocodes=promocodes,
                )

            with allure.step("Проверяем, что прайсрул обновился, ответ 200, к прайсрулу привязан новый промокод в единственном количестве"):
                check.equal(update_response.status_code, 200, "Status code should be 200")
                check.equal(promocode_value in update_response.json()["data"]["promocodes"]["values"], True, "Added promocode is in pricerule promocode values")
                check.equal(len(update_response.json()["data"]["promocodes"]["values"]), promocodes_length + 1, "Promocodes length should be +1")

    @allure.id("2329")
    @allure.title("Обновление прайсрула: валидация поля conditions")
    @allure.label("Service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, валидацию полей conditions при обновлении прайсрула""")
    def test_update_pricerule_conditions_validate(self):
        with allure.step("Cоздаем прайсрул со статусом 'pending' и типом прайсрула на способ оплаты"):
            date_start = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')
            type_id = 2
            conditions = [{"type": "paymentMethod", "operand": "in", "condition": ["sbp", "sber"]}]

            create_pricerule_response = self.api_pricerules.create(conditions=conditions, typeId=type_id,
                                                                   dateStart=date_start)
            assert create_pricerule_response.status_code == 201
            pricerule_id = create_pricerule_response.json()["data"]["id"]

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем у прайсрула способы оплаты"):
            conditions = [{"type": "paymentMethod", "operand": "in", "condition": ["cash", "podeli"]}]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
            with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
                assert update_response.status_code == 200
                assert update_response.json()["data"]["conditions"] == conditions

        with allure.step("Обновляем у прайсрула платформу"):
            conditions = [
                {"type": "platform", "operand": "in", "condition": ["app"]},
                {"type": "paymentMethod", "operand": "in", "condition": ["cash", "podeli"]},
            ]
        update_response = self.api_pricerules.update(
            pricerule_id=pricerule_id,
            current_data=pricerule_response.json()["data"],
            typeId=pricerule_response.json()["data"]["type"]["id"],
            conditions=conditions,
        )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert (
                    update_response.json()["data"]["conditions"][0] == conditions[0] or
                    update_response.json()["data"]["conditions"][0] == conditions[1]
            )
            assert (
                    update_response.json()["data"]["conditions"][1] == conditions[0] or
                    update_response.json()["data"]["conditions"][1] == conditions[1]
            )

        with allure.step("Находим прайсрул со статусом 'pending' и типом прайсрула промокод"):
            conditions = ["and date(start_at) > NOW() and type_id = 1"]
            pricerule_id = self.get_pricerule(conditions=conditions)

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем прайсрул без поля condition"):
            conditions = None
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
            with allure.step("Проверяем, что прайсрул  обновился, ответ 201"):
                assert update_response.status_code == 200
                assert update_response.json()["data"]["conditions"] == []

        with allure.step("Обновляем у прайсрула платформу"):
            conditions = [{"type": "platform", "operand": "in", "condition": ["app"]}]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["conditions"] == conditions

        with allure.step("Обновляем у прайсрула ограничение на сумму корзины"):
            conditions = [{"type": "cartSum", "operand": ">", "condition": 3001}]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["conditions"] == conditions

        with allure.step("Обновляем прайсрул с ограничениями по подборке"):
            cond = ["is_category = false and parent_id is null"]
            compilation_id, slug, gender = self.get_compilation_by_conditions(conditions=cond)
            conditions = [{"type": "compilations", "operand": "in", "condition": [int(compilation_id)]}]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            condition = update_response.json()["data"]["conditions"][0]["condition"]
            assert condition["compilations"][0]["id"] == int(compilation_id)

        with allure.step("Обновляем прайсрул с ограничениями по подборке и категории"):
            cond = ["is_category = true"]
            category_id, slug, gender = self.get_compilation_by_conditions(conditions=cond)
            conditions = [{"type": "compilations", "operand": "in", "condition": [int(compilation_id),
                                                                                  int(category_id)]}]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            condition = update_response.json()["data"]["conditions"][0]["condition"]
            assert condition["compilations"][0]["id"] == int(compilation_id)
            assert condition["categories"][0]["id"] == int(category_id)

        with allure.step("Обновляем прайсрул с большим количеством ограничений"):
            other_conditions = [
                {"type": "platform", "operand": "in", "condition": ["app", "web"]},
                {"type": "cartSum", "operand": ">=", "condition": 3002},
                {"type": "stickers", "operand": "notIn", "condition": ["new"]},
                {"type": "articles", "operand": "notIn", "condition": ["Wide9"]},
            ]
            conditions = [*conditions, *other_conditions]
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                conditions=conditions,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200


    @allure.id("2811")
    @allure.title("Обновление прайсрула: валидация поля productsListType")
    @allure.label("Service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("""Проверяем, прайсрул со статусом pending нельзя обновить без поля productsListType""")
    def test_update_pricerule_products_list_type_validate(self):
        with allure.step("Находим прайсрул со статусом 'pending'"):
            pricerule_id = utils.get_pricerule_by_status(status="pending")

        with allure.step("Получаем прайсрул через апи"):
            pricerule_response = self.api_pricerules.get(pricerule_id=pricerule_id)
            assert pricerule_response.status_code == 200

        with allure.step("Обновляем прайсрул без поля productsListType"):
            products_list_type = None
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул с пустым полем productsListType"):
            products_list_type = ""
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул со значением поля productsListType не из списка допустимых"):
            products_list_type = "qwertyu"
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type,
            )
        with allure.step("Проверяем, что прайсрул не обновился, ответ 422"):
            assert update_response.status_code == 422

        with allure.step("Обновляем прайсрул со значением поля productsListType = all"):
            products_list_type = "all"
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["productsListType"] == products_list_type

        with allure.step("Обновляем прайсрул со значением поля productsListType = compilations"):
            products_list_type = "compilations"
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["productsListType"] == products_list_type

        with allure.step("Обновляем прайсрул со значением поля productsListType = articles"):
            products_list_type = "articles"
            update_response = self.api_pricerules.update(
                pricerule_id=pricerule_id,
                current_data=pricerule_response.json()["data"],
                typeId=pricerule_response.json()["data"]["type"]["id"],
                productsListType=products_list_type,
            )
        with allure.step("Проверяем, что прайсрул обновился, ответ 200"):
            assert update_response.status_code == 200
            assert update_response.json()["data"]["productsListType"] == products_list_type


    @allure.id("2965")
    @allure.title("Обновление прайсрула: валидация значения промокода")
    @allure.label("service", "Orders")
    @allure.feature("Карточка прайсрула")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description(
        """Нельзя обновить один прайсрул с промокодом, который  активен в другом прайсруле на этот период""")
    def test_value_promocode_update(self):
        with allure.step("Создать прайсрул с одним промокодом, действующими в определенный период"):
            promocode_value_1 = Text("en").word() + str(Generic().random.randint(1, 100))

            promocodes_1 = {
                "counterType": "general",
                "counterAmount": 1,
                "values": [promocode_value_1]
            }

            dateStart_1 = datetime.today().strftime('%Y-%m-%d')
            dateEnd_1 = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')

            create_pricerule_response_1 = self.api_pricerules.create(
                dateStart=dateStart_1,
                dateEnd=dateEnd_1,
                promocodes=promocodes_1
            )

        with allure.step("Создать прайсрул с другим промокодом, который еще не начал действовать"):
            promocode_value_2 = Text("en").word() + str(Generic().random.randint(1, 100))

            promocodes_2 = {
                "counterType": "general",
                "counterAmount": 1,
                "values": [promocode_value_2]
            }

            dateStart_2 = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
            dateEnd_2 = (date.today() + timedelta(days=60)).strftime('%Y-%m-%d')

            create_pricerule_response_2 = self.api_pricerules.create(
                dateStart=dateStart_2,
                dateEnd=dateEnd_2,
                promocodes=promocodes_2
            )

        with allure.step("Проверяем, что прайсрулы создались, ответ 201"):
            check.equal( create_pricerule_response_1.status_code, 201, "Status code should be 201")
            check.equal( create_pricerule_response_2.status_code, 201, "Status code should be 201")

        with allure.step("Обновляем прайсрул 2 с промокодом, который сохранен в прайсруле 1 и с периодом, который пересечется с периодом первого прайсрула"):
            promocodes_2 = {
                "counterType": "general",
                "counterAmount": 1,
                "values": [promocode_value_1, promocode_value_2]
            }

            current_data = create_pricerule_response_2.json()["data"]
            current_data["dateStart"] =  dateStart_1
            current_data["dateEnd"] = dateEnd_1

            update_pricerule_response_2 = self.api_pricerules.update(
                    pricerule_id=create_pricerule_response_2.json()["data"]["id"],
                    current_data=current_data,
                    typeId=create_pricerule_response_2.json()["data"]["type"]["id"],
                    promocodes=promocodes_2,
                )

        with allure.step("Проверяем, что в ответе 200 и сообщение об ошибке Один из промокодов уже используется в выбранном периоде"):
            check.equal(update_pricerule_response_2.status_code, 200, "Status code should be 200")
            check.equal(update_pricerule_response_2.json()["alerts"][0]["text"], "Один из промокодов уже используется в выбранном периоде")
            check.equal(update_pricerule_response_2.json()["alerts"][0]["title"],"Повторяющийся промокод")
            check.equal(update_pricerule_response_2.json()["alerts"][0]["type"], "ERROR")


