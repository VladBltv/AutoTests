import allure
from allure_commons.types import Severity

from befree.api_model.cocreate.private import CocreatePrivate


class TestContestDelete(CocreatePrivate):
    @allure.id("2632")
    @allure.title("Удаление конкурса")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем: 
        - удаление существующей сущности
        - удаление не существующей сущности
        - при удалении конкурса с isVisibleOnMainPage = 1 приходит уведомление, что на главной больше нет конкурса
    """
    )
    def test_delete_contest(self):
        with allure.step("Создать дефолтный конкурс с размещением на главной"):
            create_contest_response = self.api_contests.create(isVisibleOnMainPage=1)
            contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Удалить созданный конкурс"):
            delete_contest_response = self.api_contests.delete(contest_id=contest_id)

        with allure.step(
            "Проверить, что ответ 200. Выводится сообщение, что на главной больше нет конкусра"
        ):
            assert delete_contest_response.status_code == 200
            assert (
                "На главной странице нет конкурсов."
                in delete_contest_response.json()["alerts"][1]["text"]
            )

        with allure.step("Удалить уже удаленный конкурс"):
            delete_contest_response = self.api_contests.delete(contest_id=contest_id)

        with allure.step("Проверить, что ответ 404"):
            assert delete_contest_response.status_code == 404

        with allure.step("Удалить не существующий конкурс"):
            delete_contest_response = self.api_contests.delete(contest_id=1000000)

        with allure.step("Проверить, что ответ 404"):
            assert delete_contest_response.status_code == 404
