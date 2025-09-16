from random import randint

import allure
from allure_commons.types import Severity
from befree.api_model import db_connection
from befree.api_model.cocreate.private import CocreatePrivate
from utils import helpers
from pytest_voluptuous import S
from befree.api_model.cocreate.private.users.schemas import cms_users_list


class TestUsersCmsList(CocreatePrivate):
    @allure.id("2665")
    @allure.title("Получение списка пользователей cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Проверяем, что апи отвечает успехом и отдает полный списко активных пользователей из базы"
    )
    def test_get_users_count(self):
        with allure.step("Запросить список пользователей в базе"):
            query = f"""
                        select u.id
                        from users u
                        where u.deleted_at is null
                        """

            users_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Запросить список пользователей в апи"):
            users_list_response = self.api_users.get_list()

        with allure.step("Статус запроса: успешно"):
            assert users_list_response.status_code == 200

        with allure.step("Проверить что количество пользователей списков совпадает"):
            assert len(users_base) == users_list_response.json()["pagination"]["total"]

    @allure.id("2666")
    @allure.title("Сортировка списка пользователей cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Пользователи отдаются в порядке убывания их id. Проверяется только первая страница"
    )
    def test_users_ordering(self):
        with allure.step("Запросить список пользователей в апи"):
            users_list_response = self.api_users.get_list(per_page=50)

        with allure.step("Проверяем что id пользователя вернулись в порядке убывания"):
            users_id = list(map(lambda x: x["id"], users_list_response.json()["data"]["users"]))
            assert helpers.is_sorted(l=users_id, direction="desc")

    @allure.id("2669")
    @allure.title("Проверка структуры ответа для списка пользователей в админке")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Проверяем, что структура ответа ЭП получения списка пользователя соответствует заданной"
    )
    def test_users_list_structure(self):
        with allure.step("Запросить список пользователей в апи"):
            users_list_response = self.api_users.get_list(per_page=10)

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(cms_users_list) == users_list_response.json()

    @allure.id("2664")
    @allure.title("Фильтрация пользователей cocreate в админке по id")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Проверяем, что можно найти пользователя по id. Поиск по данному полю осуществялется только по полному вхождению поискового запроса"
    )
    def test_filter_userss_by_id(self):
        with allure.step("Запросить список пользователей в базе"):
            query = f"""
                        select u.id, u.first_name, u.last_name , u.email 
                        from users u
                        where u.deleted_at is null
                        order by u.id desc
                        limit 50
                        """

            users_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем пользователя, по которому будем искать"):
            ref_user = users_base[0]

        with allure.step("Получаем список пользователей с запросом по id, полное вхождение"):
            users_list_response = self.api_users.get_list(query=ref_user["id"], per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого id совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="id",
                ref_value=ref_user["id"],
                data=users_list_response.json()["data"]["users"],
            )

        # with allure.step(
        #     "Получаем список пользователей с запросом по id, неполное вхождение"
        # ):
        #     users_list_response = get_users_list(
        #         auth_token,
        #         query=str(ref_user["id"])[: len(str(ref_user["id"])) // 2 * -1],
        #         per_page=50,
        #     )
        #
        #     assert any(
        #         list(
        #             map(
        #                 lambda x: x["id"] == ref_user["id"],
        #                 users_list_response.json()["data"]["users"],
        #             )
        #         )
        #     )

    @allure.id("2661")
    @allure.title("Фильтрация пользователей cocreate в админке по имени")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description("Проверяем, что можно найти пользователя по имени")
    def test_filter_users_by_first_name(self):
        with allure.step("Запросить список пользователей в базе"):
            query = f"""
                        select u.id, u.first_name, u.last_name , u.email 
                        from users u
                        where u.deleted_at is null
                        order by u.id desc
                        limit 50
                        """

            users_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем пользователя, по которому будем искать"):
            ref_user = users_base[randint(0, len(users_base) - 1)]

        with allure.step(
            "Получаем список пользователей с запросом по first_name, полное вхождение"
        ):
            users_list_response = self.api_users.get_list(query=ref_user["first_name"], per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого first_name совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="firstName",
                ref_value=ref_user["first_name"],
                data=users_list_response.json()["data"]["users"],
            )

        with allure.step(
            "Получаем список пользователей с запросом по first_name, не полное вхождение"
        ):
            users_list_response = self.api_users.get_list(
                query=ref_user["first_name"][: len(ref_user["first_name"]) // 2 * -1],
                per_page=50,
            )

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого в first_name есть частичное совпадение с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="firstName",
                ref_value=ref_user["first_name"],
                data=users_list_response.json()["data"]["users"],
            )

    @allure.id("2670")
    @allure.title("Фильтрация пользователей cocreate в админке по фамилии")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description("Проверяем, что можно найти пользователя по фамилии")
    def test_filter_users_by_last_name(self):
        with allure.step("Запросить список пользователей в базе"):
            query = f"""
                        select u.id, u.first_name, u.last_name , u.email 
                        from users u
                        where u.deleted_at is null
                        order by u.id desc
                        limit 50
                        """

            users_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем пользователя, по которому будем искать"):
            ref_user = users_base[randint(0, len(users_base) - 1)]

        with allure.step("Получаем список пользователей с запросом по last_name, полное вхождение"):
            users_list_response = self.api_users.get_list(query=ref_user["last_name"], per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого last_name совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="lastName",
                ref_value=ref_user["last_name"],
                data=users_list_response.json()["data"]["users"],
            )

        with allure.step(
            "Получаем список пользователей с запросом по last_name, не полное вхождение"
        ):
            users_list_response = self.api_users.get_list(
                query=ref_user["last_name"][: len(ref_user["last_name"]) // 2 * -1],
                per_page=50,
            )

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого в last_name есть частичное совпадение с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="lastName",
                ref_value=ref_user["last_name"],
                data=users_list_response.json()["data"]["users"],
            )

    @allure.id("2674")
    @allure.title("Фильтрация пользователей cocreate в админке по email")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description("Проверяем, что можно найти пользователя по email")
    def test_filter_users_by_email(self):
        with allure.step("Запросить список пользователей в базе"):
            query = f"""
                        select u.id, u.first_name, u.last_name , u.email 
                        from users u
                        where u.deleted_at is null
                        order by u.id desc
                        limit 50
                        """

            users_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем пользователя, по которому будем искать"):
            ref_user = users_base[randint(0, len(users_base) - 1)]

        with allure.step("Получаем список пользователей с запросом по email, полное вхождение"):
            users_list_response = self.api_users.get_list(query=ref_user["email"], per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого email совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="email",
                ref_value=ref_user["email"],
                data=users_list_response.json()["data"]["users"],
            )

        with allure.step("Получаем список пользователей с запросом по email, не полное вхождение"):
            users_list_response = self.api_users.get_list(
                query=ref_user["email"][: len(ref_user["email"]) // 2 * -1],
                per_page=50,
            )

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого в email есть частичное совпадение с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="email",
                ref_value=ref_user["email"],
                data=users_list_response.json()["data"]["users"],
            )

    @allure.id("2668")
    @allure.title("Фильтрация пользователей cocreate в админке регистронезависимая")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Проверяем, что поиск работает, даже если запрос и данные в разном регистре"
    )
    def test_filter_users_by_last_name_capitalize(self):
        with allure.step("Запросить список пользователей в базе"):
            query = f"""
                        select u.id, u.first_name, u.last_name , u.email 
                        from users u
                        where u.deleted_at is null
                        order by u.id desc
                        limit 50
                        """

            users_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем пользователя, по которому будем искать"):
            ref_user = users_base[randint(0, len(users_base) - 1)]

        with allure.step("Приводим last_name для поискового запроса в противоположный регистр"):
            if ref_user["last_name"].islower() or (
                not ref_user["last_name"].islower() and not ref_user["last_name"].isupper()
            ):
                last_name_query = ref_user["last_name"].upper()
            elif ref_user["last_name"].isupper():
                last_name_query = ref_user["last_name"].lower()

        with allure.step(
            "Получаем список пользователей с запросом по last_name в противоположном регистре, полное вхождение"
        ):
            users_list_response = self.api_users.get_list(query=last_name_query, per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть пользователь, у которого last_name совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="lastName",
                ref_value=ref_user["last_name"],
                data=users_list_response.json()["data"]["users"],
            )

    @allure.id("2675")
    @allure.title("Получение списка пользователей с запросом пагинации за пределом диапазона")
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description(
        "Проверяем, что при запросе страницы пагинации за пределами диапазона ЭП отвечает корректно"
    )
    def test_get_users_list_out_of_range(self):
        with allure.step("Запросить список пользователей в апи"):
            users_list_response = self.api_users.get_list()

        with allure.step("Определить номер последней страницы навигации"):
            last_page = users_list_response.json()["pagination"]["lastPage"]

        with allure.step("Рассчитать страницу за пределами диапазона last_page + 10"):
            out_of_range_page = last_page + 10

        with allure.step(
            "Запросить список пользователей в апи для страницы за пределами диапазона"
        ):
            users_list_response = self.api_users.get_list(page=out_of_range_page)

        with allure.step("Проверить, что ответ 200 и в данных возвращается пустой массив"):
            assert (
                users_list_response.status_code == 200
                and users_list_response.json()["data"]["users"] == []
            )

    @allure.id("2662")
    @allure.title(
        "Валидация параметра количества пользователей на странице для списка пользователей"
    )
    @allure.label("service", "Cocreate")
    @allure.feature("Список пользователей")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.description("Параметр per_page не может быть меньше 2 и больше 50 и должно быть числом")
    def test_per_page_validation(self):
        with allure.step("Запросить список пользователей в апи с количеством пользователей 1"):
            users_list_response = self.api_users.get_list(per_page=1)

        with allure.step("Проверить, что ответ 422"):
            assert users_list_response.status_code == 422

        with allure.step("Запросить список пользователей в апи с количеством пользователей 100"):
            users_list_response = self.api_users.get_list(per_page=100)

        with allure.step("Проверить, что ответ 422"):
            assert users_list_response.status_code == 422
