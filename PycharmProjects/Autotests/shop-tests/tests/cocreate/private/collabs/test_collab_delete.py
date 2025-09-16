import allure
from allure_commons.types import Severity
from befree.api_model import db_connection
from befree.api_model.cocreate.private import CocreatePrivate


class TestCollabDelete(CocreatePrivate):
    @allure.id("2594")
    @allure.title("Удаление коллаборации: существующей")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("""Проверяем, что API успешно удаляет существующую коллаборацию""")
    def test_delete_existing_active_collaboration(self):
        with allure.step("Создать дефолтную коллаборацию"):
            create_collaboration_response = self.api_collaborations.create()
            collaboration_for_deleting = create_collaboration_response.json()["data"]["id"]

        with allure.step("Отправить запрос на удаление выбранной коллаборации"):
            delete_collaboration_response = self.api_collaborations.delete(
                collaboration_id=collaboration_for_deleting
            )

        with allure.step(
            "Проверить, что коллаборация успешно удалена: успешный ответ API, в базе установилось значение deleted_at"
        ):
            query = f"""
                        select c.deleted_at 
                        from collaborations c  
                        where id = {collaboration_for_deleting}
                    """
            collaboration_for_deleting = list(
                map(lambda n: n["deleted_at"], db_connection.cocreate.get_data(query))
            )

            assert (
                delete_collaboration_response.status_code == 200
                and collaboration_for_deleting[0] is not None
            )

    @allure.id("2599")
    @allure.title("Удаление коллаборации: не существующей")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что API отдает ошибку при попытке удалить несуществующую или уже удаленную коллаборацию"""
    )
    def test_delete_unexisting_collaboration(self):
        with allure.step("Создать дефолтную коллаборацию для теста"):
            create_collaboration_response = self.api_collaborations.create()
            test_collab_id = create_collaboration_response.json()["data"]["id"]

        with allure.step("Удалить заведомо не существующую коллаборацию"):
            unexisting_collab_id = test_collab_id + 1000
            delete_collaboration_response = self.api_collaborations.delete(
                collaboration_id=unexisting_collab_id
            )

        with allure.step("Проверить, что ответ запроса 422"):
            delete_collaboration_response.status_code == 422

        with allure.step("Удалить тестовую коллаборацию"):
            self.api_collaborations.delete(collaboration_id=test_collab_id)

        with allure.step("Удалить тестовую коллаборацию еще раз"):
            delete_collaboration_response = self.api_collaborations.delete(
                collaboration_id=test_collab_id
            )

        with allure.step("Проверить, что ответ запроса 422"):
            delete_collaboration_response.status_code == 422
