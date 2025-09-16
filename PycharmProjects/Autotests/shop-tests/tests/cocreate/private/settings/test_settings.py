import random

import allure
from allure_commons.types import Severity
from befree.api_model import db_connection
from mimesis import Text
from befree.api_model.cocreate.private import CocreatePrivate


class TestSettings(CocreatePrivate):
    @allure.id("2650")
    @allure.title("Получение настроек")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description(
        """Проверяем получение настроек с фиксированными данными, которые используются для всех конкурсов"""
    )
    def test_get_settings(self):
        with allure.step("Отправить запрос на получение настроек"):
            get_settings_response = self.api_settings.get()

        with allure.step("Проверить, что ответ 200"):
            assert get_settings_response.status_code == 200

        with allure.step("Проверить, что данные в запросе совпадают с базой"):
            query = """
                select s.key, s.title, s.data as value
                from settings s 
                order by s.key asc
            """

            settings_list_db = db_connection.cocreate.get_data(query)
            settings_list_api = get_settings_response.json()["data"]["settings"]

            assert settings_list_db == settings_list_api

    @allure.id("2671")
    @allure.title("Изменение настроек")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description("""Проверяем установку и удаление значения настроек""")
    def test_define_settings(self):
        with allure.step("Отправить запрос на изменение всех настроек"):
            age = random.randint(0, 50)
            criteria = Text("ru").sentence()
            update_settings_response = self.api_settings.update(age=age, criteria=criteria)

        with allure.step("Проверить что ответ успешный и данные изменились"):
            assert update_settings_response.status_code == 200
            updated_settings_list = update_settings_response.json()["data"]["settings"]

            for i in range(0, len(updated_settings_list)):
                if updated_settings_list[i]["key"] == "age":
                    assert updated_settings_list[i]["value"] == age
                elif updated_settings_list[i]["key"] == "criteria":
                    assert updated_settings_list[i]["value"] == criteria

        with allure.step("Отправить запрос на изменение одной настройки с пустыми данными"):
            update_settings_response = self.api_settings.update(criteria="")

        with allure.step("Проверить что ответ успешный"):
            assert update_settings_response.status_code == 200

        with allure.step(
            "Проверить, что у одной настройки данные затерлись, а у остальных остались без изменения"
        ):
            get_settings_response = self.api_settings.get()
            settings = get_settings_response.json()["data"]["settings"]

            for i in range(0, len(settings)):
                if settings[i]["key"] == "age":
                    assert settings[i]["value"] == age
                elif settings[i]["key"] == "criteria":
                    assert settings[i]["value"] == None

    @allure.id("2667")
    @allure.title("Изменение настроек: валидация ограничений длины контента")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description(
        """Проверяем, что нельза задать значения текста настроек больше определенной длинны. Ограничение для обеих настроек в 400 символов """
    )
    def test_validate_settings(self):
        with allure.step(
            "Отправить запрос на изменение всех настроек c контентом более 400 символов"
        ):
            age = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлени"
            criteria = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлени"

            update_settings_response = self.api_settings.update(criteria=criteria, age=age)

        with allure.step("Проверить, что настройки не были обновлены успешно, ответ 422"):
            assert update_settings_response.status_code == 422

        with allure.step(
            "Отправить запрос на изменение всех настроек c контентом ровно 400 символов"
        ):
            age = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлен"
            criteria = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлен"

            update_settings_response = self.api_settings.update(criteria=criteria, age=age)
        with allure.step("Проверить, что настройки были обновлени успешно, ответ 200"):
            assert update_settings_response.status_code == 200
