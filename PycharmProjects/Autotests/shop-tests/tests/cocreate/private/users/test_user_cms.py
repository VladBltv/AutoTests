from random import randint

import allure
from allure_commons.types import Severity
from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate.private.users.schemas import cms_user
from befree.api_model import db_connection
from pytest_voluptuous import S


class TestUserCms(CocreatePrivate):
    @allure.id("2673")
    @allure.title("Получение детальной информации пользователя cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка пользователя")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Проверяем, что апи отвечает успехом и отдает данные по пользователю, которые содержатся в дминке"
    )
    def test_get_user_information(self):
        with allure.step("Запросить полный список id пользователей в базе"):
            query = f"""
                        select u.id
                        from users u
                        where u.deleted_at is null
                        """

            users_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Выбрать пользователя, которого будем запрашивать"):
            ref_user_id = users_base[randint(0, len(users_base) - 1)]

        with allure.step("Запросить детальную информацию пользователя по выбранному id"):
            user_response = self.api_users.get_one(user_id=ref_user_id)

        with allure.step("Проверить, что статус ответа 200"):
            assert user_response.status_code == 200

        with allure.step("Проверить, что структура ответа соответствует запроектированной"):
            assert S(cms_user) == user_response.json()

        with allure.step(
            "Проверить, что в каждом поле безусловные данные соответствуют базе. Дописать проверку через код"
        ):
            ...

    @allure.id("2660")
    @allure.title("Проверка данных о том, является ли пользователь креатором или голосующим")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка пользователя")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        """Проверяем, что апи отдает верную информацию о том, является ли пользователь креатором или голосующим. 
        Креатором является пользователь, у которого есть хотя бы одна не удаленная работа в таблице works. 
        Голосующим является пользовтель, у которого в таблице likes есть записи с работами, которые не удалены"""
    )
    def test_get_user_creator_voter_information(self):
        with allure.step("Получить id всех пользователей"):
            query_users = f"""
                        select u.id
                        from users u
                        where u.deleted_at is null
                        """

            users = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query_users)))

        with allure.step("Получить id всех пользователей, кто является креатором"):
            query_creators = f"""
                        select distinct w.user_id
                        from works w
                        left join users u on u.id = w.user_id
                        where u.deleted_at is null and w.deleted_at is null
                        """

            creators = list(
                map(lambda n: n["user_id"], db_connection.cocreate.get_data(query_creators))
            )

        with allure.step("Получить id всех пользователей, кто является голосующим"):
            query_voters = f"""
                                select distinct l.user_id
                                from likes l
                                left join users u on u.id = l.user_id
                                left join works w on w.id = l.work_id
                                where u.deleted_at is null and w.deleted_at is null
                                """

            voters = list(
                map(lambda n: n["user_id"], db_connection.cocreate.get_data(query_voters))
            )

        with allure.step("Найти пользователя, который не креатор "):
            not_creators = list(set(users).difference(set(creators)))
            user_response_not_creator = self.api_users.get_one(
                user_id=not_creators[randint(0, len(not_creators) - 1)]
            )

        with allure.step("Проверить, что isCreator: false"):
            assert user_response_not_creator.json()["data"]["isCreator"] is False

        with allure.step("Найти пользователя, который креатор"):
            user_response_creator = self.api_users.get_one(
                user_id=creators[randint(0, len(creators) - 1)]
            )

        with allure.step("Проверить, что isCreator: true"):
            assert user_response_creator.json()["data"]["isCreator"] is True

        with allure.step("Найти пользователя, который не голосующий"):
            not_voters = list(set(users).difference(set(voters)))
            user_response_not_voter = self.api_users.get_one(
                user_id=not_voters[randint(0, len(not_voters) - 1)]
            )

        with allure.step("Проверить, что isVoter: false"):
            assert user_response_not_voter.json()["data"]["isVoter"] is False

        with allure.step("Найти пользователя, который голосующий"):
            user_response_voter = self.api_users.get_one(
                user_id=voters[randint(0, len(voters) - 1)]
            )

        with allure.step("Проверить, что isVoter: true"):
            assert user_response_voter.json()["data"]["isVoter"] is True
