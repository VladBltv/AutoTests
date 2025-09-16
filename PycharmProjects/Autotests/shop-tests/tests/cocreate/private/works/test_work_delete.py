import allure
from allure_commons.types import Severity
from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate.public import CocreatePublic
from befree.api_model import db_connection


class TestWorkDelete(CocreatePublic, CocreatePrivate):
    @allure.id("2676")
    @allure.title("Удаление существующей работы")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Works")
    @allure.feature("Карточка работы")
    def test_delete_existing_work(self):
        with allure.step("Создать работу"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru", password="aA123456"
            )
            create_work_response = self.api_works_pub.create(
                token=user_login_response.json()["data"]["token"]
            )
            assert create_work_response.status_code == 201

            work_id = create_work_response.json()["data"]["id"]

        with allure.step("Удалить работу"):
            delete_work_response = self.api_works.delete(work_id=work_id)

        with allure.step("Проверить, что статус запроса 200"):
            delete_work_response.status_code == 200

        with allure.step("Проверить, что в базе у работы проставлена дата удаления"):
            query = f"""
                select w.deleted_at
                from works w
                where w.id = {work_id}
            """

            assert db_connection.cocreate.get_data(query)[0]["deleted_at"] is not None
