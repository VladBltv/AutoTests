import allure
from allure_commons.types import Severity
from pytest_voluptuous import S
from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate.public import CocreatePublic
from befree.api_model.cocreate.private.works.schemas import cms_work


class TestWorkShow(CocreatePrivate, CocreatePublic):
    @allure.id("2398")
    @allure.title("Просмотр работы в админке")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Works")
    @allure.feature("Карточка работы")
    @allure.description("""Проверяем, доступность работы в админке""")
    def test_get_exixting_work(self):
        with allure.step("Создать работу"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru", password="aA123456"
            )
            create_work_response = self.api_works_pub.create(
                token=user_login_response.json()["data"]["token"]
            )
            assert create_work_response.status_code == 201

        with allure.step("Запросить созданную работу"):
            get_work_response = self.api_works.get_one(
                work_id=create_work_response.json()["data"]["id"]
            )
            assert get_work_response.status_code == 200

        with allure.step("Структура ответа соответствует запроектированной"):
            assert S(cms_work) == get_work_response.json()

    @allure.id("2399")
    @allure.title("Просмотр несуществующей или удаленной работы в админке")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Works")
    @allure.feature("Карточка работы")
    @allure.description(
        """При обращении к несуществующей или удаленной работе, возвращается обработанная ошибка"""
    )
    def test_get_unexixting_work(self):
        with allure.step("Запросить заведомо несуществующую работу"):
            get_work_response = self.api_works.get_one(work_id=1000000)

        with allure.step("Проверить, что в ответе статус 404"):
            assert get_work_response.status_code == 404

        with allure.step("Запросить удаленную работу"):
            with allure.step("Создать работу"):
                user_login_response = self.api_users_pub.login(
                    email="sunny208@yandex.ru", password="aA123456"
                )
                create_work_response = self.api_works_pub.create(
                    token=user_login_response.json()["data"]["token"]
                )
                work_id = create_work_response.json()["data"]["id"]

            with allure.step("Удалить созданную работу"):
                delete_work_response = self.api_works.delete(work_id=work_id)

            with allure.step("Запросить удаленную работу"):
                get_work_response = self.api_works.get_one(work_id=work_id)

            with allure.step("Проверить, что в ответе статус 404"):
                assert get_work_response.status_code == 404

    @allure.id("2400")
    @allure.title("Просмотр скрытой работы в админке")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Works")
    @allure.feature("Карточка работы")
    @allure.description("""В админке можно посмотреть скрытую работу""")
    def test_get_hidden_work(self):
        with allure.step("Создать работу"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru", password="aA123456"
            )
            create_work_response = self.api_works_pub.create(
                token=user_login_response.json()["data"]["token"]
            )
            work_id = create_work_response.json()["data"]["id"]

        with allure.step("Скрыть работу"):
            self.api_works.update(
                work_id=work_id,
                visible=False,
                current_data=self.api_works.get_one(work_id=work_id).json()["data"],
            )

        with allure.step("Запросить скрытую работу"):
            get_work_response = self.api_works.get_one(work_id=work_id)

        with allure.step("Проверить, что статус ответа 200. В параметре is_visible приходит false"):
            assert get_work_response.status_code == 200
            assert get_work_response.json()["data"]["visible"] == False

    """
    Просмотр работы без лайков
    - приходит 0 - ок
    """

    """
    Просмотр работы без причины отклонения
    - приходит null - ок
    """

    """
    Просмотр работы / конкурс
    - если конкурс есть, то приходит он - ок
    - если конкурса нет, то приходит null - ок
    """
