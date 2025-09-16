from random import randint
import allure
from allure_commons.types import Severity
from befree.api_model import db_connection
from pytest_voluptuous import S
from befree.api_model.cocreate.private import CocreatePrivate
from utils import helpers
from befree.api_model.cocreate.private.contests.schemas import cms_contests_list


class TestContestCMSList(CocreatePrivate):
    @allure.id("2651")
    @allure.title("Получение списка конкурсов cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        "Проверяем, что апи отвечает успехом и отдает полный список конкурсов из базы"
    )
    def test_get_contests_count(self):
        with allure.step("Запросить список конкурсов в базе"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null
                    """

            contests_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Запросить список конкурсов в апи"):
            contests_list_response = self.api_contests.get_list()

        with allure.step("Статус запроса: успешно"):
            assert contests_list_response.status_code == 200

        with allure.step("Проверить что количество конкурсов списков совпадает"):
            assert len(contests_base) == contests_list_response.json()["pagination"]["total"]

    @allure.id("2659")
    @allure.title("Проверка структуры ответа для списка конкурсов в админке")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        "Проверяем, что структура ответа ЭП получения списка конкурсов соответствует заданной"
    )
    def test_contests_list_structure(self):
        with allure.step("Запросить список конкурсов в апи"):
            contests_list_response = self.api_contests.get_list()

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(cms_contests_list) == contests_list_response.json()

    @allure.id("2646")
    @allure.title("Сортировка списка конкурсов cocreate")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        "Конкурсы отдаются в порядке убывания их id. Сначала идут активные конкурсы, затем не активные. Проверяется только первая страница"
    )
    def test_contests_ordering(self):
        with allure.step("Запросить список конкурсов в базе"):
            query = f"""
                        select c.id, c.is_visible 
                        from contests c 
                        where c.deleted_at is null
                        order by c.is_visible desc, c.id desc
                        limit 50
                    """

            contests_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Запросить список конкурсов в апи"):
            contests_list_response = self.api_contests.get_list(per_page=50)

            contests_id = list(
                map(lambda x: x["id"], contests_list_response.json()["data"]["contests"])
            )

        with allure.step(
            "Проверяем что id конкурсов вернулись в порядке убывания сначала для активных, затем для неактивных"
        ):
            assert contests_id == contests_base

    @allure.id("2657")
    @allure.title("Фильтрация конкурсов в админке по статусу active")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """При фильтрации по статусу конкурса active отдаются все не удаленные конкурсы, у которых флаг is_visible=true и статус не archived"""
    )
    def test_contests_list_active(self):
        with allure.step("Запросить список конкурсов в базе, соответствующих фильтру"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null and c.is_visible is true and c.status not in ('archived')
                        order by c.id desc
                        limit 50
                    """

            contests_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Запросить список конкурсов в апи c фильтром active"):
            contests_list_response = self.api_contests.get_list(visibility="active", per_page=50)
            contests_id = list(
                map(lambda x: x["id"], contests_list_response.json()["data"]["contests"])
            )

        with allure.step("Проверить что id конкурсов из апи соответствуют id базы"):
            assert contests_base == contests_id

    @allure.id("2658")
    @allure.title("Фильтрация конкурсов в админке по статусу hidden")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """При фильтрации по статусу конкурса hidden отдаются все не удаленные конкурсы, у которых флаг is_visible=false"""
    )
    def test_contests_list_hidden(self):
        with allure.step("Запросить список конкурсов в базе, соответствующих фильтру"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null and c.is_visible is false
                        order by c.id desc
                        limit 50
                    """

            contests_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Запросить список конкурсов в апи c фильтром hidden"):
            contests_list_response = self.api_contests.get_list(visibility="hidden", per_page=50)
            contests_id = list(
                map(lambda x: x["id"], contests_list_response.json()["data"]["contests"])
            )

        with allure.step("Проверить что id конкурсов из апи соответствуют id базы"):
            assert contests_base == contests_id

    @allure.id("2649")
    @allure.title("Фильтрация конкурсов в админке по статусу archival")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """При фильтрации по статусу конкурса archival отдаются все не удаленные конкурсы, у которых статус archived"""
    )
    def test_contests_list_archival(self):
        with allure.step("Запросить список конкурсов в базе, соответствующих фильтру"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null and c.status in ('archived')
                        order by c.is_visible desc, c.id desc
                        limit 50
                    """

            contests_base = list(map(lambda n: n["id"], db_connection.cocreate.get_data(query)))

        with allure.step("Запросить список конкурсов в апи c фильтром archival"):
            contests_list_response = self.api_contests.get_list(visibility="archival", per_page=50)
            contests_id = list(
                map(lambda x: x["id"], contests_list_response.json()["data"]["contests"])
            )

        with allure.step("Проверить что id конкурсов из апи соответствуют id базы"):
            assert contests_base == contests_id

    @allure.id("2654")
    @allure.title("Фильтрация конкурсов cocreate в админке по названию")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description("Проверяем, что можно найти конкурс по полю title")
    def test_filter_contests_by_title(self):
        with allure.step("Запросить список конкурсов в базе"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null
                        order by c.id desc
                        limit 50
                    """

            contests_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем конкурс, по которому будем искать"):
            ref_contest = contests_base[randint(0, len(contests_base) - 1)]
            get_contest_response = self.api_contests.get_one(contest_id=ref_contest["id"])
            ref_title = get_contest_response.json()["data"]["title"]

        with allure.step("Получаем список конкурсов с запросом по названию, полное вхождение"):
            contests_list_response = self.api_contests.get_list(query=ref_title, per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть конкурс, у которого title совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="title",
                ref_value=ref_title,
                data=contests_list_response.json()["data"]["contests"],
            )

        with allure.step("Получаем список конкурсов с запросом по title, не полное вхождение"):
            contests_list_response = self.api_contests.get_list(
                query=ref_title[: len(ref_title) // 2 * -1],
                per_page=50,
            )

        with allure.step(
            "Проверяем, что в ответе есть конкурс, у которого в title есть частичное совпадение с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="title",
                ref_value=ref_title,
                data=contests_list_response.json()["data"]["contests"],
            )

    @allure.id("2653")
    @allure.title("Фильтрация конкурсов cocreate в админке по id")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description("Проверяем, что можно найти конкурс по полю id")
    def test_filter_contests_by_id(self):
        with allure.step("Запросить список конкурсов в базе"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null
                        order by c.id desc
                        limit 50
                    """

            contests_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем конкурс, по которому будем искать"):
            ref_contest = contests_base[randint(0, len(contests_base) - 1)]

        with allure.step("Получаем список конкурсов с запросом по id, полное вхождение"):
            contests_list_response = self.api_contests.get_list(
                query=ref_contest["id"], per_page=50
            )

        with allure.step(
            "Проверяем, что в ответе есть конкурс, у которого id совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="id",
                ref_value=ref_contest["id"],
                data=contests_list_response.json()["data"]["contests"],
            )

    @allure.id("2648")
    @allure.title("Фильтрация конкурсов cocreate в админке по названию регистронезависимая")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        "Проверяем, что можно найти конкурс по полю title используя в запросе противоположный регистр"
    )
    def test_filter_contests_by_title_capitalize(self):
        with allure.step("Запросить список конкурсов в базе"):
            query = f"""
                        select c.id
                        from contests c 
                        where c.deleted_at is null
                        order by c.id desc
                        limit 50
                    """

            contests_base = db_connection.cocreate.get_data(query)

        with allure.step("Выбираем конкурс, по которому будем искать"):
            ref_contest = contests_base[randint(0, len(contests_base) - 1)]
            get_contest_response = self.api_contests.get_one(contest_id=ref_contest["id"])
            ref_title = get_contest_response.json()["data"]["title"]

        with allure.step("Приводим название для поискового запроса в противоположный регистр"):
            if ref_title.islower() or (not ref_title.islower() and not ref_title.isupper()):
                title_query = ref_title.upper()
            elif ref_title.isupper():
                title_query = ref_title.lower()

        with allure.step(
            "Получаем список конкурсов с запросом по названию в противоположном регистре, полное вхождение"
        ):
            contests_list_response = self.api_contests.get_list(query=title_query, per_page=50)

        with allure.step(
            "Проверяем, что в ответе есть конкурс, у которого title совпадает с переданным"
        ):
            assert helpers.is_exists_in_data_list(
                ref_key="title",
                ref_value=ref_title,
                data=contests_list_response.json()["data"]["contests"],
            )

    @allure.id("2655")
    @allure.title("Валидация на фильтрацию конкурсов по видимости")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        "Проверяем, параметр visibility не принимает значения отличные от: active, hidden, archival"
    )
    def test_validation_filter_visibility(self):
        with allure.step(
            "Отправить запрос на получение конкурсов с проивзольным значением visibility"
        ):
            contests_list_response = self.api_contests.get_list(visibility="anystatus", per_page=50)

        with allure.step("Проверить что статус ответа 422"):
            assert contests_list_response.status_code == 422

    @allure.id("2663")
    @allure.title("Получение списка конкурсов с запросом пагинации за пределом диапазона")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        "Проверяем, что при запросе страницы пагинации за пределами диапазона ЭП отвечает корректно"
    )
    def test_get_contests_list_out_of_range(self):
        with allure.step("Запросить список конкурсов в апи"):
            contests_list_response = self.api_contests.get_list()

        with allure.step("Определить номер последней страницы навигации"):
            last_page = contests_list_response.json()["pagination"]["lastPage"]

        with allure.step("Рассчитать страницу за пределами диапазона last_page + 10"):
            out_of_range_page = last_page + 10

        with allure.step("Запросить список конкурсов в апи для страницы за пределами диапазона"):
            contests_list_response = self.api_contests.get_list(page=out_of_range_page)

        with allure.step("Проверить, что ответ 200 и в данных возвращается пустой массив"):
            assert (
                contests_list_response.status_code == 200
                and contests_list_response.json()["data"]["contests"] == []
            )

    @allure.id("2656")
    @allure.title("Валидация параметра количества записей на странице для списка конкурсов")
    @allure.label("service", "Cocreate")
    @allure.feature("Список конкурсов")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description("Параметр per_page не может быть меньше 2 и больше 50 и должно быть числом")
    def test_per_page_validation(self):
        with allure.step("Запросить список конкурсов в апи с количеством записей 1"):
            contests_list_response = self.api_contests.get_list(per_page=1)

        with allure.step("Проверить, что ответ 422"):
            assert contests_list_response.status_code == 422

        with allure.step("Запросить список конкурсов в апи с количеством записей 100"):
            contests_list_response = self.api_contests.get_list(per_page=100)

        with allure.step("Проверить, что ответ 422"):
            assert contests_list_response.status_code == 422
