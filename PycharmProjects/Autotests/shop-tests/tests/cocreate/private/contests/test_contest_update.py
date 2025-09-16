import allure
from allure_commons.types import Severity
from mimesis import Internet
from datetime import datetime, timedelta

from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate import utils as utils_cocreate

from utils.data_generation import rand_str
from utils.database import filling_out_table


class TestContestUpdate(CocreatePrivate):
    @allure.id("2631")
    @allure.title("Нельзя обновить несуществующий или удаленный конкурс")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """При обновлении несуществующего или удаленного конкурса возникает 404 ошибка"""
    )
    def test_update_unexisting_contest(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Обновить заведомо не существующий конкурс"):
            unexisting_contest_id = test_contest_id + 1000
            update_contest_response = self.api_contests.update(contest_id=unexisting_contest_id)

        with allure.step("Проверить, что ответ запроса 404"):
            assert update_contest_response.status_code == 404

        with allure.step("Удалить тестовый конкурс"):
            self.api_contests.delete(contest_id=test_contest_id)

        with allure.step("Обновить удаленный конкурс"):
            update_contest_response = self.api_contests.update(contest_id=test_contest_id)

        with allure.step("Проверить, что ответ запроса 404"):
            assert update_contest_response.status_code == 404

    @allure.id("2633")
    @allure.title("Обновление конкурса: валидация поля title")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля title и с данными длинной более 255 символов"""
    )
    def test_update_contest_title_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля title"):
            title = None

        with allure.step("Обновляем конкурс без title"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                title=title,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обновления конкурса с пустым полем title"):
            title = ""

        with allure.step("Обновляем конкурс с пустым полем title"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                title=title,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем title длиннее 255 символов"
        ):
            title = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и форм"

        with allure.step("Обновляем конкурс c полем title длиннее 255 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                title=title,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем title ровно 255 символов"
        ):
            title = (
                "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и фор",
            )

        with allure.step("Обновляем конкурс c полем title ровно 255 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                title=title,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2634")
    @allure.title("Обновление конкурса: валидация поля announcement")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля announcement и с данными длинной более 150 символов"""
    )
    def test_update_contest_announcement_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля announcement"):
            announcement = None

        with allure.step("Обновляем конкурс без announcement"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                announcement=announcement,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обновления конкурса с пустым полем announcement"):
            announcement = ""

        with allure.step("Обновляем конкурс с пустым полем announcement"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                announcement=announcement,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем announcement длиннее 150 символов"
        ):
            announcement = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XV"

        with allure.step("Обновляем конкурс c полем announcement длиннее 150 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                announcement=announcement,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем announcement ровно 150 символов"
        ):
            announcement = (
                "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала X",
            )

        with allure.step("Обновляем конкурс c полем announcement ровно 150 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                announcement=announcement,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2635")
    @allure.title("Обновление конкурса: валидация поля concept")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля concept и с данными длинной более 600 символов"""
    )
    def test_update_contest_concept_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля concept"):
            concept = None

        with allure.step("Обновляем конкурс без concept"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                concept=concept,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обновления конкурса с пустым полем concept"):
            concept = ""

        with allure.step("Обновляем конкурс с пустым полем concept"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                concept=concept,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем concept длиннее 600 символов"
        ):
            concept = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать смДля успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать смДля успешного выступления на конкурсе необходима тщательная подготовка. Важ"

        with allure.step("Обновляем конкурс c полем concept длиннее 600 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                concept=concept,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем concept ровно 600 символов"
        ):
            concept = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать смДля успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать смДля успешного выступления на конкурсе необходима тщательная подготовка. Ва",
            )

        with allure.step("Обновляем конкурс c полем concept ровно 600 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                concept=concept,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2636")
    @allure.title("Обновление конкурса: валидация поля conditions")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля conditions и с данными длинной более 400 символов"""
    )
    def test_update_contest_conditions_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля conditions"):
            conditions = None

        with allure.step("Обновить конкурс без conditions"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                conditions=conditions,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обновления конкурса с пустым полем conditions"):
            conditions = ""

        with allure.step("Обновляем конкурс с пустым полем conditions"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                conditions=conditions,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем conditions длиннее 400 символов"
        ):
            conditions = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлени"

        with allure.step("Обновляем конкурс c полем conditions длиннее 400 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                conditions=conditions,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем conditions ровно 400 символов"
        ):
            conditions = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлен",
            )

        with allure.step("Обновляем конкурс c полем conditions ровно 400 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                conditions=conditions,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2637")
    @allure.title("Обновление конкурса: валидация поля skills")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля skills и с данными длинной более 400 символов"""
    )
    def test_update_contest_skills_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля skills"):
            skills = None

        with allure.step("Обновляем конкурс без skills"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                skills=skills,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обновления конкурса с пустым полем skills"):
            skills = ""

        with allure.step("Обновляем конкурс с пустым полем skills"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                skills=skills,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем skills длиннее 400 символов"
        ):
            skills = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлени"

        with allure.step("Обновляем конкурс c полем skills длиннее 400 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                skills=skills,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем skills ровно 400 символов"
        ):
            skills = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореаПомните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации. Для успешного выступлен",
            )

        with allure.step("Обновляем конкурс c полем skills ровно 400 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                skills=skills,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2638")
    @allure.title("Обновление конкурса: валидация поля prize")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля prize и с данными длинной более 200 символов"""
    )
    def test_update_contest_prize_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля prize"):
            prize = None

        with allure.step("Обновляем конкурс без prize"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                prize=prize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обновления конкурса с пустым полем prize"):
            prize = ""

        with allure.step("Обновляем конкурс с пустым полем prize"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                prize=prize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем prize длиннее 200 символов"
        ):
            prize = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про кр. Для успешного выступления на конкурсе необходима"

        with allure.step("Обновляем конкурс c полем prize длиннее 200 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                prize=prize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем prize ровно 200 символов"
        ):
            prize = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про кр. Для успешного выступления на конкурсе необходим",
            )

        with allure.step("Обновляем конкурс c полем prize ровно 200 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                prize=prize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2639")
    @allure.title("Обновление конкурса: валидация поля audiencePrize")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя обновить конкурс без поля audiencePrize и с данными длинной более 200 символов"""
    )
    def test_update_contest_audience_prize_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля prize"):
            audiencePrize = None

        with allure.step("Обновляем конкурс без audiencePrize"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                audiencePrize=audiencePrize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для обвновления конкурса с пустым полем prize"):
            audiencePrize = ""

        with allure.step("Обновляем конкурс с пустым полем audiencePrize"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                audiencePrize=audiencePrize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем audiencePrize длиннее 200 символов"
        ):
            audiencePrize = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про кр. Для успешного выступления на конкурсе необходима"

        with allure.step("Обновляем конкурс c полем praudiencePrizeize длиннее 200 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                audiencePrize=audiencePrize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса c полем audiencePrize ровно 200 символов"
        ):
            audiencePrize = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про кр. Для успешного выступления на конкурсе необходим",
            )

        with allure.step("Обновляем конкурс c полем audiencePrize ровно 200 символов"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                audiencePrize=audiencePrize,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2640")
    @allure.title("Обновление конкурса: валидация поля slug")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
         - можно обновить конкурс без поля slug (поле отсутствует совсем или пустое значение), 
         - если значение не отправляется, то данные генерируются из поля title
         - нельзя задать слаг для конкурса, если в базе уже есть не удаленный (возможно инвизибл) конкурс 
         с таким значением slug
         - можно задать конкурсу слаг, который уже есть в базе, но только, если прежний конкурс удален
         """
    )
    def test_update_contest_slug_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create(
                title=f"Random contest title {rand_str}"
            )
            test_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для обновления конкурса без поля slug"):
            slug = None

        with allure.step("Обновляем конкурс без slug"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                slug=slug,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

        with allure.step("Подготовить данные для обновления конкурса с пустым slug"):
            slug = ""

        with allure.step("Обновляем конкурс с пустым slug"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                slug=slug,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс обновился, ответ 200"):
            assert update_contest_response.status_code == 200

        with allure.step("Подготовить данные для нового конкурса с определенным slug"):
            slug = Internet().slug(parts_count=4)

        with allure.step("Создаем референсный конкурс с конретным slug"):
            create_contest_response = self.api_contests.create(slug=slug)
            ref_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Обновляем первый конкурс с уже существующим slug"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                slug=slug,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что первый конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Скрыть референсный конкурс"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            self.api_contests.update(
                contest_id=ref_contest_id,
                visible=0,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Обновляем первый конкурс со slug, совпадающим со скрытым конкурсом"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                slug=slug,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не обновился, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Удалить референсный конкурс"):
            self.api_contests.delete(contest_id=ref_contest_id)

        with allure.step("Обновляем первый конкурс со slug, совпадающим с удаленным конкурсом"):
            get_contest_response = self.api_contests.get_one(contest_id=test_contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=test_contest_id,
                slug=slug,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс успешно обновился, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2641")
    @allure.title("Обновление конкурса: валидация поля referees")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
         - нельзя обновить конкурс без поля referees (поле отсутствует совсем или пустое значение), 
         - максимально можно установить 6 пользователей
         - если передать двух одинаковых, то данные в ответе апи не дублируются
         """
    )
    def test_update_contest_referees_validate(self):
        with allure.step("Создать конкурс для проверки "):
            create_contest_response = self.api_contests.create()
            contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Подготовить данные для конкурса без поля referees"):
            referees = None

        with allure.step("Обновить конкурс без referees"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id,
                referees=referees,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для конкурса с пустым полем referees"):
            referees = [""]

        with allure.step("Обновить конкурс с пустым полем referees"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id,
                referees=referees,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полем referees с одинаковыми значениями"
        ):
            users_response = self.api_users.get_list()
            user_id = users_response.json()["data"]["users"][0]["id"]
            referees = [user_id, user_id]

        with allure.step("Обновить конкурс с полем referees с одинаковыми значениями"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id,
                referees=referees,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс был обновлен успешно, ответ 200"):
            assert (
                update_contest_response.status_code == 200
                and len(update_contest_response.json()["data"]["referees"]) == 1
                and update_contest_response.json()["data"]["referees"][0]["id"] == user_id
            )

        with allure.step("Подготовить данные для конкурса с полем referees длиной более 6"):
            users_response = self.api_users.get_list(per_page=7)
            referees = list(map(lambda n: n["id"], users_response.json()["data"]["users"]))

        with allure.step("Обновить конкурс с полем referees длиной более 6"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id,
                referees=referees,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Подготовить данные для конкурса с полем referees длиной ровно 6"):
            users_response = self.api_users.get_list(per_page=6)
            referees = list(map(lambda n: n["id"], users_response.json()["data"]["users"]))

        with allure.step("Обновить конкурс с полем referees длиной ровно 6"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id,
                referees=referees,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверяем, что конкурс был обновлен успешно, ответ 200"):
            assert update_contest_response.status_code == 200

    @allure.id("2642")
    @allure.title("Обновление конкурса: валидация поля dates")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
        - не обязательные
            - если не передать, то остаются записанными предыдущие значения
        - принимается только специальный формат
        - можно обновить только если конкурс в статусе announce
        - now < start < endOfAcceptanceOfWork <= finish
            - дата старта в текущий день по времени меньше настоящего - не обновляется
            - дата старта в текущий день по времени больше настоящего - обновляется
            - дата старта больше даты приема работ - не обновляется
            - дата старта больше даты окончания - не обновляется
            - дата приема работ равна дате окончания полностью - обновляется
            - дата приема работ больше даты окончания по минутам - не обновляется
            - дата окончания между датами начала и приема работ - не обновляется
            - любая дата: несуществующая - не обновляется
         """
    )
    def test_update_contest_dates_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            contest_id = create_contest_response.json()["data"]["id"]
            dates_initial = create_contest_response.json()["data"]["dates"]

        with allure.step("Подготовить данные для обновления конкурса без полей с датами"):
            dates = None

        with allure.step("Отправить запрос на обновление без поля dates"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step(
            "Проверить, что конкурс был обновлен успешно, ответ 200. В сущности конкурса остались те же самые даты"
        ):
            dates_after_updating = update_contest_response.json()["data"]["dates"]
            assert (
                update_contest_response.status_code == 200 and dates_after_updating == dates_initial
            )

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат в неверном формате"
        ):
            dates = {
                "start": (datetime.today() + timedelta(1)).strftime(
                    "%m-%Y-%dT00:00"
                ),  # изменен порядок следования год и месяца
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%d"
                ),  # нет минут и секунд
                "finish": (datetime.today() + timedelta(20)).strftime(
                    "%Y %m %dT00:00"
                ),  # разделитель не тире, а пробел
            }

        with allure.step("Отправить запрос на обновление конкурса с полями дат в неверном формате"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата начала меньше текущей"
        ):
            dates = {
                "start": (datetime.today() - timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }
        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата начала меньше текущей"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата начала в текущий день, но по времени больше настоящего"
        ):
            dates = {
                "start": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата начала в текущий день но по времени больше настоящего"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс  был обновлен обновлен, ответ 200"):
            assert update_contest_response.status_code == 200

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата начала больше даты окончания приема работ"
        ):
            dates = {
                "start": (datetime.now() + timedelta(15)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата начала больше даты окончания приема работ"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс  не был обновлен, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата начала больше даты окончания конкурса"
        ):
            dates = {
                "start": (datetime.now() + timedelta(30)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата начала больше даты окончания конкурса"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс  не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата окончания приема работа полностью равна дате окончания конкурса"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата окончания приема работа полностью равна дате окончания конкурса"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс был обновлен успешно, ответ 200"):
            assert update_contest_response.status_code == 200

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата приема работ больше даты окончания по минутам"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (
                    datetime.today() + timedelta(days=10, minutes=30)
                ).strftime("%Y-%m-%dT%H:%M"),
                "finish": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата приема работ больше даты окончания по минутам"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс был не обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат где дата окончания между датами начала и приема работ"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.now() + timedelta(20)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на обновление конкурса с полями дат где дата окончания между датами начала и приема работ"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления конкурса с полями дат для попытки обновления конкурса не в статусе announce"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.now() + timedelta(30)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(40)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step("Установить конкурсу статус start"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("start", contest_id)],
            }

            filling_out_table(data, "cocreate")

        with allure.step(
            "Отправить запрос на обновление дат конкурса, который находится в статусе start"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Установить конкурсу статус voting"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("voting", contest_id)],
            }
            filling_out_table(data, "cocreate")

        with allure.step(
            "Отправить запрос на обновление дат конкурса, который находится в статусе voting"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Установить конкурсу статус counting"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("counting", contest_id)],
            }

            filling_out_table(data, "cocreate")

        with allure.step(
            "Отправить запрос на обновление дат конкурса, который находится в статусе counting"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что конкурс не был обновлен успешно, ответ 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Установить конкурсу статус archived"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            dates_before_update = get_contest_response.json()["data"]["dates"]

            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("archived", contest_id)],
            }

            filling_out_table(data, "cocreate")

        with allure.step(
            "Отправить запрос на обновление дат конкурса, который находится в статусе archived"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, dates=dates, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Провеить, что ответ 200, но даты не изменились"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            dates_after_update = get_contest_response.json()["data"]["dates"]

            assert (
                update_contest_response.status_code == 200
                and dates_before_update == dates_after_update
            )

    @allure.id("2643")
    @allure.title("Обновление конкурса: валидация изображений")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
        - не обязательные
            - если не передать, то остаются записанными предыдущие значения
            - при загрузке новых - обновляются на новые
         """
    )
    def test_update_contest_images_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            contest_id = create_contest_response.json()["data"]["id"]
            initial_images = create_contest_response.json()["data"]["images"]

        with allure.step("Обновить конкурс без изменения изображений"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, images=None, current_data=get_contest_response.json()["data"]
            )
            images_after_update = self.api_contests.get_one(contest_id=contest_id).json()["data"][
                "images"
            ]

        with allure.step("Проверить, что конкурс успешно обновился"):
            assert update_contest_response.status_code == 200

        with allure.step("Проверить, что изображения те же самые"):
            assert initial_images == images_after_update

        with allure.step("Подготовить новые изображения для конкурса"):
            images = utils_cocreate.set_contest_images(
                desktop="contest-desktop-jpg.jpg",
                mobile="contest-mobile-jpg.jpg",
                main="contest-main-jpg.jpg",
            )

        with allure.step("Обновить конкурс с изменением изображений"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response_2 = self.api_contests.update(
                contest_id=contest_id,
                images=images,
                current_data=get_contest_response.json()["data"],
            )
            images_after_update_2 = self.api_contests.get_one(contest_id=contest_id).json()["data"][
                "images"
            ]

        with allure.step("Проверить, что конкурс успешно обновился"):
            assert update_contest_response_2.status_code == 200

        with allure.step("Проверить, что изображения новые"):
            assert initial_images != images_after_update_2

    @allure.id("2644")
    @allure.title("Обновление конкурса: валидация файла с правилами")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
        - не обязательные
            - если не передать, то остается прежний файл
            - при загрузке нового - обновляются на новый
         """
    )
    def test_update_contest_rules_validate(self):
        with allure.step("Создать дефолтный конкурс для теста"):
            create_contest_response = self.api_contests.create()
            contest_id = create_contest_response.json()["data"]["id"]
            initial_rules = create_contest_response.json()["data"]["rules"]

        with allure.step("Обновить конкурс без изменения правил"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, rules=None, current_data=get_contest_response.json()["data"]
            )
            rules_after_update = self.api_contests.get_one(contest_id=contest_id).json()["data"][
                "rules"
            ]

        with allure.step("Проверить, что конкурс успешно обновился"):
            assert update_contest_response.status_code == 200

        with allure.step("Проверить, что праивла те же самые"):
            assert initial_rules == rules_after_update

        with allure.step("Подготовить новые правила для конкурса"):
            rules = utils_cocreate.set_contest_rules(rules="rules-doc.doc")

        with allure.step("Обновить конкурс с изменением правил"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response_2 = self.api_contests.update(
                contest_id=contest_id, rules=rules, current_data=get_contest_response.json()["data"]
            )
            rules_after_update_2 = self.api_contests.get_one(contest_id=contest_id).json()["data"][
                "rules"
            ]

        with allure.step("Проверить, что конкурс успешно обновился"):
            assert update_contest_response_2.status_code == 200

        with allure.step("Проверить, что изображения новые"):
            assert initial_rules != rules_after_update_2

    @allure.id("2645")
    @allure.title("Обновление конкурса: валидация видимости")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что: 
        - поле обязательное - без него конкурс не обновляется
        - 1: делается активным
        - 0: делается не активным
        - При деактивации конкурса, выведенного на главной, приходит уведомленеи, что на главной больше нет конкурсов
    """
    )
    def test_update_contest_visibility_validate(self):
        with allure.step("Отправить запрос на создание конкурса по умолчанию"):
            create_contest_response = self.api_contests.create()
            contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Отправить запрос на обновление конкурса без параметра visible"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id,
                visible=None,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверить, что статус запроса 422"):
            assert update_contest_response.status_code == 422

        with allure.step("Отправить запрос на обновление конкурса с параметром visible=0"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, visible=0, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что статус запроса 200. У конкурса видимость False"):
            assert update_contest_response.status_code == 200
            assert update_contest_response.json()["data"]["visible"] == False

        with allure.step("Отправить запрос на обновление конкурса с параметром visible=1"):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id)
            update_contest_response = self.api_contests.update(
                contest_id=contest_id, visible=1, current_data=get_contest_response.json()["data"]
            )

        with allure.step("Проверить, что статус запроса 200. У конкурса видимость True"):
            assert update_contest_response.status_code == 200
            assert update_contest_response.json()["data"]["visible"] == True

        with allure.step(
            "При деактивации конкурса, выведенного на главной, приходит уведомленеи, что на главной больше нет конкурсов"
        ):
            with allure.step("Установить у конкурса  isVisibleOnMainPage = 1"):
                get_contest_response = self.api_contests.get_one(contest_id=contest_id)
                update_contest_response = self.api_contests.update(
                    contest_id=contest_id,
                    isVisibleOnMainPage=1,
                    current_data=get_contest_response.json()["data"],
                )

            with allure.step("Установить у конкурса visible = 0"):
                get_contest_response = self.api_contests.get_one(contest_id=contest_id)
                update_contest_response = self.api_contests.update(
                    contest_id=contest_id,
                    visible=0,
                    current_data=get_contest_response.json()["data"],
                )

            with allure.step("Выводится сообщение, что на главной больше нет конкурсов"):
                assert (
                    "На главной странице нет конкурсов."
                    in update_contest_response.json()["alerts"][1]["text"]
                )

    @allure.id("2652")
    @allure.title("Обновление конкурса: валидация вывода на главной")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что: 
        - поле обязательное - без него конкурс не обновляется
        - 1: делается видимым на главной
        - 0: делается не видимым на главной
        - при замене у конкурса параметра isVisibleOnMainPage с 1 на 0 приходит уведомление, что на главной больше нет конкурса
        - менять параметр можно у конкурса в любом статусе, даже у архивного
    """
    )
    def test_update_contest_show_on_main_validate(self):
        with allure.step(
            "Отправить запрос на создание конкурса по умолчанию с isVisibleOnMainPage = 0"
        ):
            create_contest_response_1 = self.api_contests.create()
            contest_id_1 = create_contest_response_1.json()["data"]["id"]

        with allure.step("Отправить запрос на создание конкурса с isVisibleOnMainPage = 1"):
            create_contest_response_2 = self.api_contests.create(isVisibleOnMainPage=1)
            contest_id_2 = create_contest_response_2.json()["data"]["id"]

        with allure.step(
            "Отправить запрос на обновление конкурса 1 без параметра isVisibleOnMainPage"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_1)
            update_contest_response_1 = self.api_contests.update(
                contest_id=contest_id_1,
                isVisibleOnMainPage=None,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверить, что статус запроса 422"):
            assert update_contest_response_1.status_code == 422

        with allure.step(
            "Отправить запрос на обновление конкурса 1 с параметром isVisibleOnMainPage=1"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_1)
            update_contest_response_1 = self.api_contests.update(
                contest_id=contest_id_1,
                isVisibleOnMainPage=1,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step(
            "Проверить, что статус запроса 200. У конкурса 1 вывод на главной True. Приходит сообщение, что конкурс 2 скрыт с главной"
        ):
            assert update_contest_response_1.status_code == 200
            assert update_contest_response_1.json()["data"]["isVisibleOnMainPage"] == True

            assert (
                "скрыт с главной страницы" in update_contest_response_1.json()["alerts"][1]["text"]
                and f"{contest_id_2}" in update_contest_response_1.json()["alerts"][1]["text"]
            )
            assert (
                self.api_contests.get_one(contest_id=contest_id_2).json()["data"][
                    "isVisibleOnMainPage"
                ]
                == 0
            )

        with allure.step(
            "Отправить запрос на обновление конкурса 1 с параметром isVisibleOnMainPage=0"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_1)
            update_contest_response_1 = self.api_contests.update(
                contest_id=contest_id_1,
                isVisibleOnMainPage=0,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step(
            "Проверить, что статус запроса 200. У конкурса вывод на главной False. Выводится сообщение, что на главной больше нет конкурсов"
        ):
            assert update_contest_response_1.status_code == 200
            assert update_contest_response_1.json()["data"]["isVisibleOnMainPage"] == False
            assert (
                "На главной странице нет конкурсов."
                in update_contest_response_1.json()["alerts"][1]["text"]
            )

        # установка у архивного конкурса напрмяую
        with allure.step("Перевести конкурс 1  в статус archived"):
            data = {
                "table": "contests",
                "field_name": ["status"],
                "record_identifier": "id",
                "data": [("archived", contest_id_1)],
            }

            filling_out_table(data, "cocreate")

        with allure.step(
            "Отправить запрос на обновление конкурса 1 с параметром isVisibleOnMainPage=1"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_1)
            update_contest_response_1 = self.api_contests.update(
                contest_id=contest_id_1,
                isVisibleOnMainPage=1,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Проверить, что статус запроса 200. У конкурса 1 вывод на главной True."):
            assert update_contest_response_1.status_code == 200
            assert update_contest_response_1.json()["data"]["isVisibleOnMainPage"] == True

        # Снятие у архивного конкурса напрямую
        with allure.step(
            "Отправить запрос на обновление конкурса 1 с параметром isVisibleOnMainPage=0"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_1)
            update_contest_response_1 = self.api_contests.update(
                contest_id=contest_id_1,
                isVisibleOnMainPage=0,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step(
            "Проверить, что статус запроса 200. У конкурса вывод на главной False. Выводится сообщение, что на главной больше нет конкурсов"
        ):
            assert update_contest_response_1.status_code == 200
            assert update_contest_response_1.json()["data"]["isVisibleOnMainPage"] == False
            assert (
                "На главной странице нет конкурсов."
                in update_contest_response_1.json()["alerts"][1]["text"]
            )

        # Снятие у архивного конкурса опосредованно
        with allure.step(
            "Отправить запрос на обновление конкурса 1 с параметром isVisibleOnMainPage=1"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_1)
            update_contest_response_1 = self.api_contests.update(
                contest_id=contest_id_1,
                isVisibleOnMainPage=1,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step(
            "Отправить запрос на обновление конкурса 2 с параметром isVisibleOnMainPage=1"
        ):
            get_contest_response = self.api_contests.get_one(contest_id=contest_id_2)
            update_contest_response_2 = self.api_contests.update(
                contest_id=contest_id_2,
                isVisibleOnMainPage=1,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step(
            "Проверить, что статус запроса 200. У конкурса 2 вывод на главной True. Приходит сообщение, что конкурс 1 скрыт с главной"
        ):
            assert update_contest_response_2.status_code == 200
            assert update_contest_response_2.json()["data"]["isVisibleOnMainPage"] == True

            assert (
                "скрыт с главной страницы" in update_contest_response_2.json()["alerts"][1]["text"]
                and f"{contest_id_1}" in update_contest_response_2.json()["alerts"][1]["text"]
            )
            assert (
                self.api_contests.get_one(contest_id=contest_id_1).json()["data"][
                    "isVisibleOnMainPage"
                ]
                == 0
            )
