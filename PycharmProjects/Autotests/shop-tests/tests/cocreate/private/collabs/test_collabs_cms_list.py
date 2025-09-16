from random import randint
import allure
from allure_commons.types import Severity
from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate.private.collaborations.schemas import cms_collaborations_list
from befree.api_model import db_connection
from pytest_voluptuous import S
from utils import helpers


class TestCollabsCmsList(CocreatePrivate):
    @allure.id("2615")
    @allure.title("Получение списка коллабораций cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        "Проверяем, что апи отвечает успехом и отдает полный список коллабораций из базы"
    )
    def test_get_collaborations_count(self):
        with allure.step("Запросить список коллабораций в базе"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is null
                    """

            collaborations_base = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

        with allure.step("Запросить список коллабораций в апи"):
            collaborations_list_response = self.api_collaborations.get_list()

        with allure.step("Статус запроса: успешно"):
            assert collaborations_list_response.status_code == 200

        with allure.step("Проверить, что количество коллабораций в списках совпадает"):
            assert (
                len(collaborations_base)
                == collaborations_list_response.json()["pagination"]["total"]
            )

    @allure.id("2608")
    @allure.title("Проверка структуры ответа для списка коллабораций в админке")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        "Проверяем, что структура ответа ЭП получения списка коллабораций соответствует заданной"
    )
    def test_collaborations_list_structure(self):
        with allure.step("Запросить список коллабораций в апи"):
            collaborations_list_response = self.api_collaborations.get_list()

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(cms_collaborations_list) == collaborations_list_response.json()

    @allure.id("2224")
    @allure.title("Сортировка списка коллабораций cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        "Коллаборации отдаются в порядке убывания их id. Сначала идут активные Коллаборации, затем не активные. Проверяется только первая страница"
    )
    def test_collaborations_ordering(self):
        with allure.step("Запросить список коллабораций в базе"):
            query = f"""
                        select c.id, c.is_visible 
                        from collaborations c 
                        where c.deleted_at is null
                        order by c.is_visible desc, c.id desc
                        limit 50
                    """

            collaborations_base = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

        with allure.step("Запросить список коллабораций в апи"):
            collaborations_list_response = self.api_collaborations.get_list(per_page=50)

            collaborations_id = list(
                map(
                    lambda x: x["id"],
                    collaborations_list_response.json()["data"]["collaborations"],
                )
            )

        with allure.step(
            "Проверяем что id коллабораций вернулись в порядке убывания сначала для активных, затем для неактивных"
        ):
            assert collaborations_id == collaborations_base

    @allure.id("2607")
    @allure.title("Фильтрация коллабораций в админке по статусу active")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """При фильтрации по статусу коллаборации active отдаются все не удаленные Коллаборации, у которых флаг is_visible=true"""
    )
    def test_collaborations_list_active(self):
        with allure.step("Запросить список коллабораций в базе, соответствующих фильтру"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is null and c.is_visible is true
                        order by c.id desc
                        limit 50
                    """

            collaborations_base = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

        with allure.step("Запросить список коллабораций в апи c фильтром active"):
            collaborations_list_response = self.api_collaborations.get_list(
                visibility="active", per_page=50
            )
            collaborations_id = list(
                map(
                    lambda x: x["id"],
                    collaborations_list_response.json()["data"]["collaborations"],
                )
            )

        with allure.step("Проверить что id коллабораций из апи соответствуют id базы"):
            assert collaborations_base == collaborations_id

    @allure.id("2617")
    @allure.title("Фильтрация коллабораций в админке по статусу hidden")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """При фильтрации по статусу коллаборации hidden отдаются все не удаленные коллаборации, у которых флаг is_visible=false"""
    )
    def test_collaborations_list_hidden(self):
        with allure.step("Запросить список коллабораций в базе, соответствующих фильтру"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is null and c.is_visible is false
                        order by c.id desc
                        limit 50
                    """

            collaborations_base = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

        with allure.step("Запросить список коллабораций в апи c фильтром hidden"):
            collaborations_list_response = self.api_collaborations.get_list(
                visibility="hidden", per_page=50
            )
            collaborations_id = list(
                map(
                    lambda x: x["id"],
                    collaborations_list_response.json()["data"]["collaborations"],
                )
            )

        with allure.step("Проверить что id коллабораций из апи соответствуют id базы"):
            assert collaborations_base == collaborations_id

    @allure.id("2613")
    @allure.title("Фильтрация коллабораций cocreate в админке по названию")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("Проверяем, что можно найти коллаборацию по полю title")
    def test_filter_collaborations_by_title(self):
        with allure.step("Запросить список коллабораций в базе"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is null
                        order by c.id desc
                        limit 50
                    """

            collaborations_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем коллаборацию, по которому будем искать и запоминаем ее title"):
            ref_collab = collaborations_base[randint(0, len(collaborations_base) - 1)]
            ref_collab_title = self.api_collaborations.get_one(
                collaboration_id=ref_collab["id"]
            ).json()["data"]["title"]

        with allure.step("Получаем список коллабораций с запросом по названию, полное вхождение"):
            collaborations_list_response = self.api_collaborations.get_list(
                query=ref_collab_title, per_page=50
            )

        with allure.step(
            "Проверяем, что в ответе есть коллаборацию, у которого title совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="title",
                ref_value=ref_collab_title,
                data=collaborations_list_response.json()["data"]["collaborations"],
            )

        with allure.step("Получаем список коллабораций с запросом по title, не полное вхождение"):
            collaborations_list_response = self.api_collaborations.get_list(
                query=ref_collab_title[: len(ref_collab_title) // 2 * -1],
                per_page=50,
            )

        with allure.step(
            "Проверяем, что в ответе есть коллаборацию, у которого в title есть частичное совпадение с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="title",
                ref_value=ref_collab_title,
                data=collaborations_list_response.json()["data"]["collaborations"],
            )

    @allure.id("2616")
    @allure.title("Фильтрация коллабораций cocreate в админке по id")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("Проверяем, что можно найти коллаборацию по полю id")
    def test_filter_collaborations_by_id(self):
        with allure.step("Запросить список коллабораций в базе"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is null
                        order by c.id desc
                        limit 50
                    """

            collaborations_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем коллаборацию, по которому будем искать"):
            ref_collab = collaborations_base[randint(0, len(collaborations_base) - 1)]

        with allure.step("Получаем список коллабораций с запросом по id, полное вхождение"):
            collaborations_list_response = self.api_collaborations.get_list(
                query=ref_collab["id"], per_page=50
            )

        with allure.step(
            "Проверяем, что в ответе есть коллаборацию, у которого id совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="id",
                ref_value=ref_collab["id"],
                data=collaborations_list_response.json()["data"]["collaborations"],
            )

    @allure.id("2613")
    @allure.title("Фильтрация коллабораций cocreate в админке по названию регистронезависимая")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        "Проверяем, что поиск по полю title работает, если регистр запроса отличается от регистра искомого значения"
    )
    def test_filter_collaborations_by_title_capitalize(self):
        with allure.step("Запросить список коллабораций в базе"):
            query = f"""
                        select c.id
                        from collaborations c 
                        where c.deleted_at is null
                        order by c.id desc
                        limit 50
                    """

            collaborations_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем коллаборацию, по которому будем искать и запоминаем ее тайтл"):
            ref_collab = collaborations_base[randint(0, len(collaborations_base) - 1)]
            ref_collab_title = self.api_collaborations.get_one(
                collaboration_id=ref_collab["id"]
            ).json()["data"]["title"]

        with allure.step("Приводим название для поискового запроса в противоположный регистр"):
            if ref_collab_title.islower() or (
                not ref_collab_title.islower() and not ref_collab_title.isupper()
            ):
                title_query = ref_collab_title.upper()
            elif ref_collab_title.isupper():
                title_query = ref_collab_title.lower()

        with allure.step(
            "Получаем список коллабораций с запросом по названию в противоположном регистре, полное вхождение"
        ):
            collaborations_list_response = self.api_collaborations.get_list(
                query=title_query, per_page=50
            )

        with allure.step(
            "Проверяем, что в ответе есть коллаборация, у которой title совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="title",
                ref_value=ref_collab_title,
                data=collaborations_list_response.json()["data"]["collaborations"],
            )

    @allure.id("2611")
    @allure.title("Валидация на фильтрацию коллабораций по видимости")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        "Проверяем, параметр visibility не принимает значения отличные от: active, hidden"
    )
    def test_validation_filter_visibility(self):
        with allure.step(
            "Отправить запрос на получение коллабораций с проивзольным значением visibility"
        ):
            collaborations_list_response = self.api_collaborations.get_list(
                visibility="anystatus", per_page=50
            )

        with allure.step("Проверить что статус ответа 422"):
            assert collaborations_list_response.status_code == 422

    @allure.id("2612")
    @allure.title("Получение списка коллабораций с запросом пагинации за пределом диапазона")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        "Проверяем, что при запросе страницы пагинации за пределами диапазона ЭП отвечает корректно"
    )
    def test_get_collaborations_list_out_of_range(self):
        with allure.step("Запросить список коллабораций в апи"):
            collaborations_list_response = self.api_collaborations.get_list()

        with allure.step("Определить номер последней страницы навигации"):
            last_page = collaborations_list_response.json()["pagination"]["lastPage"]

        with allure.step("Рассчитать страницу за пределами диапазона last_page + 10"):
            out_of_range_page = last_page + 10

        with allure.step("Запросить список коллабораций в апи для страницы за пределами диапазона"):
            collaborations_list_response = self.api_collaborations.get_list(page=out_of_range_page)

        with allure.step("Проверить, что ответ 200 и в данных возвращается пустой массив"):
            assert (
                collaborations_list_response.status_code == 200
                and collaborations_list_response.json()["data"]["collaborations"] == []
            )

    @allure.id("2614")
    @allure.title("Валидация параметра количества записей на странице для списка коллабораций")
    @allure.label("service", "Cocreate")
    @allure.feature("Список коллабораций")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("Параметр per_page не может быть меньше 2 и больше 50 и должно быть числом")
    def test_per_page_validation(self):
        with allure.step("Запросить список коллабораций в апи с количеством записей 1"):
            collaborations_list_response = self.api_collaborations.get_list(per_page=1)

        with allure.step("Проверить, что ответ 422"):
            assert collaborations_list_response.status_code == 422

        with allure.step("Запросить список коллабораций в апи с количеством записей 100"):
            collaborations_list_response = self.api_collaborations.get_list(per_page=100)

        with allure.step("Проверить, что ответ 422"):
            assert collaborations_list_response.status_code == 422
