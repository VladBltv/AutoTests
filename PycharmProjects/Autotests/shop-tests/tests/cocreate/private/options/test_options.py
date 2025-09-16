import allure
from allure_commons.types import Severity
from befree.api_model.cocreate.private import CocreatePrivate


class TestOptions(CocreatePrivate):
    @allure.id("2672")
    @allure.title("Получение опций для параметров коллабораций и конкурсов")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description(
        """Проверяем получение фиксированного списка опций, которые используются для установки параметров в коллаборациях и конкурсах"""
    )
    def test_get_options(self):
        with allure.step("Отправить запрос на получение опций"):
            get_options_response = self.api_options.get()

        with allure.step("Проверить, что ответ 200"):
            assert get_options_response.status_code == 200

        with allure.step("Проверить, что ответ содержит верные данные"):
            options_data = {
                "collaborations": {
                    "types": [
                        {"key": "art", "value": "Art"},
                        {"key": "better_future", "value": "Better future"},
                        {"key": "brands", "value": "Brands"},
                        {"key": "digital", "value": "Digital"},
                        {"key": "hub", "value": "hub"},
                        {"key": "influence", "value": "influence"},
                    ],
                    "displayTypes": [
                        {"key": "withProducts", "value": "С товарами"},
                        {"key": "withoutProducts", "value": "Без товаров"},
                    ],
                }
            }

            assert get_options_response.json()["data"] == options_data
