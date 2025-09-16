import json

import allure
from allure_commons.types import Severity
from befree.api_model.cocreate.private import CocreatePrivate


class TestMenuGet(CocreatePrivate):
    @allure.title("Получение меню админки cocreate")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем, что ЭП меню доступен и отдает верные данные")
    def test_menu_get(self):
        with allure.step("Запросить ЭП меню"):
            get_menu_response = self.api_menu.get()

        with allure.step("Проверить, что ЭП меню отдает 200 код"):
            assert get_menu_response.status_code == 200

        with allure.step("Проверить, что ответ содержит верные данные"):
            menu_data = [
                {
                    "icon-image": "/images/main-menu/cocreate.svg",
                    "items": [
                        {"icon-image": None, "items": None, "key": "contests", "name": "Конкурсы", "uri": "/contests"},
                        {"icon-image": None, "items": None, "key": "collaborations", "name": "Уже сделано", "uri": "/collaborations"},
                        {"icon-image": None, "items": None, "key": "gallery", "name": "Галерея", "uri": "/gallery"},
                        {"icon-image": None, "items": None, "key": "users", "name": "Пользователи", "uri": "/users"},
                        {"icon-image": None, "items": None, "key": "settings", "name": "Общие настройки", "uri": "/settings"},
                    ],
                    "key": "co.create",
                    "name": "Co:create",
                    "uri": "/",
                }
            ]

            assert get_menu_response.json()["data"]["menu"] == menu_data
