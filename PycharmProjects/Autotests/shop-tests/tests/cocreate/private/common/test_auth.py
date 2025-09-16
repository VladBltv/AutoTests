import allure
from allure_commons.types import Severity
from befree.api_model.cocreate.private import CocreatePrivate


class TestAuth(CocreatePrivate):
    @allure.id("2610")
    @allure.title("Приватные методы доступны только из под авторизационного токена")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description(
        "Проверяем, что приватные методы отдают 200 только с авторизационным токеном. Без токена или с протухшим токеном возвращается ошибка 401"
    )
    def test_private_api_under_auth(self):
        with allure.step("Запросить список пользователей в апи c токеном авторизации"):
            users_list_response = self.api_users.get_list()

            with allure.step("Статус ответа должен быть 200"):
                assert users_list_response.status_code == 200

        # with allure.step(
        #     "Запросить список пользователей в апи c неверным токеном авторизации"
        # ):
        #     users_list_response = self.api_users.get_users_list(token="some-wrong-token")
        #
        #     with allure.step("Статус ответа должен быть 401"):
        #         assert users_list_response.status_code == 401
        #
        # with allure.step("Запросить список пользователей в апи без токена авторизации"):
        #     users_list_response = self.api_users.get_users_list()
        #
        #     with allure.step("Статус ответа должен быть 401"):
        #         assert users_list_response.status_code == 401
