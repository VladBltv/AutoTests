from random import randint
import allure
from allure_commons.types import Severity
from befree.api_model import db_connection
from befree.api_model.cocreate.private import CocreatePrivate


class TestCollabShow(CocreatePrivate):
    @allure.id("2595")
    @allure.title("Просмотр коллаборации: существующей, активной")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("""Проверяем, что API отдает данные по активной сущестующей коллаборации""")
    def test_view_existing_collaboration(self):
        with allure.step("Получить список активных коллабораций"):
            collaborations_list_response = self.api_collaborations.get_list()
            collaborations_id = list(
                map(
                    lambda n: n["id"],
                    collaborations_list_response.json()["data"]["collaborations"],
                )
            )

        with allure.step("Выбрать рандомную коллаборацию"):
            collaboration_number = randint(0, len(collaborations_id) - 1)

        with allure.step("Запросить детальную страницу одной из коллабораций"):
            collaboration_response = self.api_collaborations.get_one(
                collaboration_id=collaborations_id[collaboration_number]
            )

        with allure.step("Проверить, что запрос отдает 200"):
            assert collaboration_response.status_code == 200

    @allure.id("2597")
    @allure.title("Просмотр коллаборации: не существуующей или не активной")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что API отдает 404 при запросе несуществующей или удаленной коллаборации"""
    )
    def test_view_unexisting_collaboration(self):
        with allure.step("Определить несуществующую коллаборацию"):
            query = f"""
                        select c.id
                        from collaborations c 
                        order by c.id desc
                        limit 1
                    """

            collaboration_last = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

            collaboration_unexisting = collaboration_last[0] + 1

        with allure.step("Запросить несуществующую коллаборацию"):
            collaboration_response = self.api_collaborations.get_one(
                collaboration_id=collaboration_unexisting
            )

        with allure.step("Проверить, что запрос отдает 404"):
            assert collaboration_response.status_code == 404

        with allure.step("Найти удаленную коллаборацию или удалить одну из существующих"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is not null
                        limit 1
                    """

            collaboration_deleted = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

            if len(collaboration_deleted) == 0:
                self.api_collaborations.delete(collaboration_id=collaboration_last[0])
                collaboration_deleted = collaboration_last[0]

        with allure.step("Запросить удаленную коллаборацию"):
            collaboration_response = self.api_collaborations.get_one(
                collaboration_id=collaboration_deleted
            )

        with allure.step("Проверить, что запрос отдает 404"):
            assert collaboration_response.status_code == 404
