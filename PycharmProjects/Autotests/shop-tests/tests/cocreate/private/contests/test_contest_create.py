from datetime import datetime, timedelta

import allure
from allure_commons.types import Severity
from mimesis import Internet
from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate import utils as utils_cocreate


class TestContestCreate(CocreatePrivate):
    @allure.id("2225")
    @allure.title("Создание конкурса: валидация поля title")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля title и с данными длинной более 255 символов"""
    )
    def test_create_contest_title_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля title"):
            title = None

        with allure.step("Создаем конкурс без title"):
            create_contest_response = self.api_contests.create(title=title)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем title"):
            title = ""

        with allure.step("Создаем конкурс с пустым полем title"):
            create_contest_response = self.api_contests.create(title=title)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем title длиннее 255 символов"
        ):
            title = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и форм"

        with allure.step("Создаем конкурс c полем title длиннее 255 символов"):
            create_contest_response = self.api_contests.create(title=title)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса c полем title ровно 255 символов"):
            title = (
                "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и фор",
            )

        with allure.step("Создаем конкурс c полем title ровно 255 символов"):
            create_contest_response = self.api_contests.create(title=title)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2618")
    @allure.title("Создание конкурса: валидация поля announcement")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля announcement и с данными длинной более 150 символов"""
    )
    def test_create_contest_announcement_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля announcement"):
            announcement = None

        with allure.step("Создаем конкурс без announcement"):
            create_contest_response = self.api_contests.create(announcement=announcement)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем announcement"):
            announcement = ""

        with allure.step("Создаем конкурс с пустым полем announcement"):
            create_contest_response = self.api_contests.create(announcement=announcement)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем announcement длиннее 150 символов"
        ):
            announcement = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XV"

        with allure.step("Создаем конкурс c полем announcement длиннее 150 символов"):
            create_contest_response = self.api_contests.create(announcement=announcement)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем announcement ровно 150 символов"
        ):
            announcement = (
                "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала X",
            )

        with allure.step("Создаем конкурс c полем announcement ровно 150 символов"):
            create_contest_response = self.api_contests.create(announcement=announcement)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2619")
    @allure.title("Создание конкурса: валидация поля concept")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля concept и с данными длинной более 600 символов"""
    )
    def test_create_contest_concept_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля concept"):
            concept = None

        with allure.step("Создаем конкурс без concept"):
            create_contest_response = self.api_contests.create(concept=concept)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем concept"):
            concept = ""

        with allure.step("Создаем конкурс с пустым полем concept"):
            create_contest_response = self.api_contests.create(concept=concept)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем concept длиннее 600 символов"
        ):
            concept = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать см Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны,Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определитьп"

        with allure.step("Создаем конкурс c полем concept длиннее 600 символов"):
            create_contest_response = self.api_contests.create(concept=concept)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем concept ровно 600 символов"
        ):
            concept = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать см Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны,Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить",
            )

        with allure.step("Создаем конкурс c полем concept ровно 600 символов"):
            create_contest_response = self.api_contests.create(concept=concept)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2620")
    @allure.title("Создание конкурса: валидация поля conditions")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля conditions и с данными длинной более 400 символов"""
    )
    def test_create_contest_conditions_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля conditions"):
            conditions = None

        with allure.step("Создаем конкурс без conditions"):
            create_contest_response = self.api_contests.create(conditions=conditions)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем conditions"):
            conditions = ""

        with allure.step("Создаем конкурс с пустым полем conditions"):
            create_contest_response = self.api_contests.create(conditions=conditions)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем conditions длиннее 400 символов"
        ):
            conditions = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самор"

        with allure.step("Создаем конкурс c полем conditions длиннее 400 символов"):
            create_contest_response = self.api_contests.create(conditions=conditions)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем conditions ровно 400 символов"
        ):
            conditions = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для само",
            )

        with allure.step("Создаем конкурс c полем conditions ровно 400 символов"):
            create_contest_response = self.api_contests.create(conditions=conditions)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2621")
    @allure.title("Создание конкурса: валидация поля skills")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля skills и с данными длинной более 400 символов"""
    )
    def test_create_contest_skills_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля skills"):
            skills = None

        with allure.step("Создаем конкурс без skills"):
            create_contest_response = self.api_contests.create(skills=skills)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем skills"):
            skills = ""

        with allure.step("Создаем конкурс с пустым полем skills"):
            create_contest_response = self.api_contests.create(skills=skills)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем skills длиннее 400 символов"
        ):
            skills = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самор"

        with allure.step("Создаем конкурс c полем skills длиннее 400 символов"):
            create_contest_response = self.api_contests.create(skills=skills)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем skills ровно 400 символов"
        ):
            skills = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про креативный подход. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для самореализации.Для успешного выступления. Помните, что участие в конкурсе - это не только шанс победить, но и отличная возможность для само",
            )

        with allure.step("Создаем конкурс c полем skills ровно 400 символов"):
            create_contest_response = self.api_contests.create(skills=skills)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2622")
    @allure.title("Создание конкурса: валидация поля prize")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля prize и с данными длинной более 200 символов"""
    )
    def test_create_contest_prize_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля prize"):
            prize = None

        with allure.step("Создаем конкурс без prize"):
            create_contest_response = self.api_contests.create(prize=prize)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем prize"):
            prize = ""

        with allure.step("Создаем конкурс с пустым полем prize"):
            create_contest_response = self.api_contests.create(prize=prize)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем prize длиннее 200 символов"
        ):
            prize = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про крДля успешного выступления на конкурсе необходима т"

        with allure.step("Создаем конкурс c полем prize длиннее 200 символов"):
            create_contest_response = self.api_contests.create(prize=prize)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса c полем prize ровно 200 символов"):
            prize = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про крДля успешного выступления на конкурсе необходимар",
            )

        with allure.step("Создаем конкурс c полем prize ровно 200 символов"):
            create_contest_response = self.api_contests.create(prize=prize)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2623")
    @allure.title("Создание конкурса: валидация поля audiencePrize")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что нельзя создать конкурс без поля audiencePrize и с данными длинной более 200 символов"""
    )
    def test_create_contest_audience_prize_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля prize"):
            audiencePrize = None

        with allure.step("Создаем конкурс без audiencePrize"):
            create_contest_response = self.api_contests.create(audiencePrize=audiencePrize)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем prize"):
            audiencePrize = ""

        with allure.step("Создаем конкурс с пустым полем audiencePrize"):
            create_contest_response = self.api_contests.create(audiencePrize=audiencePrize)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем audiencePrize длиннее 200 символов"
        ):
            audiencePrize = "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про крДля успешного выступления на конкурсе необходима т"

        with allure.step("Создаем конкурс c полем praudiencePrizeize длиннее 200 символов"):
            create_contest_response = self.api_contests.create(audiencePrize=audiencePrize)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса c полем audiencePrize ровно 200 символов"
        ):
            audiencePrize = (
                "Для успешного выступления на конкурсе необходима тщательная подготовка. Важно определить свои сильные стороны, разработать стратегию и не забыть про крДля успешного выступления на конкурсе необходимаа",
            )

        with allure.step("Создаем конкурс c полем audiencePrize ровно 200 символов"):
            create_contest_response = self.api_contests.create(audiencePrize=audiencePrize)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2624")
    @allure.title("Создание конкурса: валидация поля slug")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
         - можно создать конкурс без поля slug (поле отсутствует совсем или пустое значение), 
         - если значение не отправляется, то данные генерируются из поля title
         - нельзя создать два конкурса с одинаковым slug
         """
    )
    def test_create_contest_slug_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля slug"):
            slug = None

        with allure.step("Создаем конкурс без slug"):
            create_contest_response = self.api_contests.create(slug=slug)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

        with allure.step("Подготовить данные для нового конкурса с пустым slug"):
            slug = ""

        with allure.step("Создаем конкурс с пустым slug"):
            create_contest_response = self.api_contests.create(slug=slug)

        with allure.step("Проверяем, что конкурс создался, ответ 201"):
            assert create_contest_response.status_code == 201

        with allure.step("Подготовить данные для нового конкурса с определенным slug"):
            slug = Internet().slug(parts_count=4)

        with allure.step("Создаем референсный конкурс с конретным slug"):
            create_contest_response = self.api_contests.create(slug=slug)
            ref_contest_id = create_contest_response.json()["data"]["id"]

        with allure.step("Создаем следующий конкурс с уже существующим slug"):
            create_contest_response = self.api_contests.create(slug=slug)

        with allure.step("Проверяем, что новый конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Скрыть первый референсный конкурс"):
            get_contest_response = self.api_contests.get_one(contest_id=ref_contest_id)
            self.api_contests.update_config(
                contest_id=ref_contest_id,
                visible=0,
                current_data=get_contest_response.json()["data"],
            )

        with allure.step("Создаем конкурс со slug, совпадающим со скрытым конкурсом"):
            create_contest_response = self.api_contests.create(slug=slug)

        with allure.step("Проверяем, что конкурс не создался, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Удалить первый референсный конкурс"):
            self.api_contests.delete(contest_id=ref_contest_id)

        with allure.step("Создаем конкурс со slug, совпадающим с удаленным конкурсом"):
            create_contest_response = self.api_contests.create(slug=slug)

        with allure.step("Проверяем, что конкурс успешно создался, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2625")
    @allure.title("Создание конкурса: валидация поля referees")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
         - нельзя создать конкурс без поля referees (поле отсутствует совсем или пустое значение), 
         - максимально можно установить 6 пользователей
         - если передать двух одинаковых, то данные в ответе апи не дублируются
         """
    )
    def test_create_contest_referees_validate(self):
        with allure.step("Подготовить данные для нового конкурса без поля referees"):
            referees = None

        with allure.step("Создаем конкурс без referees"):
            create_contest_response = self.api_contests.create(referees=referees)

        with allure.step("Проверяем, что конкурс не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с пустым полем referees"):
            referees = [""]

        with allure.step("Создаем конкурс с пустым полем referees"):
            create_contest_response = self.api_contests.create(referees=referees)

        with allure.step("Проверяем, что конкурс не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полем referees с одинаковыми значениями"
        ):
            users_response = self.api_users.get_list()
            user_id = users_response.json()["data"]["users"][0]["id"]
            referees = [user_id, user_id]

        with allure.step("Создаем конкурс с полем referees с одинаковыми значениями"):
            create_contest_response = self.api_contests.create(referees=referees)

        with allure.step("Проверяем, что конкурс был создан успешно, ответ 201"):
            assert (
                create_contest_response.status_code == 201
                and len(create_contest_response.json()["data"]["referees"]) == 1
                and create_contest_response.json()["data"]["referees"][0]["id"] == user_id
            )

        with allure.step("Подготовить данные для нового конкурса с полем referees длиной более 6"):
            users_response = self.api_users.get_list(per_page=7)
            referees = list(map(lambda n: n["id"], users_response.json()["data"]["users"]))

        with allure.step("Создаем конкурс с полем referees длиной более 6"):
            create_contest_response = self.api_contests.create(referees=referees)

        with allure.step("Проверяем, что конкурс не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с полем referees длиной ровно 6"):
            users_response = self.api_users.get_list(per_page=6)
            referees = list(map(lambda n: n["id"], users_response.json()["data"]["users"]))

        with allure.step("Создаем конкурс с полем referees длиной ровно 6"):
            create_contest_response = self.api_contests.create(referees=referees)

        with allure.step("Проверяем, что конкурс был создан успешно, ответ 201"):
            assert create_contest_response.status_code == 201

    @allure.id("2628")
    @allure.title("Создание конкурса: валидация поля dates")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что:
        - поля обязательные
        - принимается только специальный формат 
        - now < start < endOfAcceptanceOfWork <= finish
            - дата старта в текущий день по времени меньше настоящего - не создается
            - дата старта в текущий день по времени больше настоящего - создается
            - дата старта больше даты приема работ - не создается
            - дата старта больше даты окончания - не создается
            - дата приема работ равна дате окончания полностью - создается
            - дата приема работ больше даты окончания по минутам - не создается
            - дата окончания между датами начала и приема работ - не создается
            - любая дата: несуществующая - не создается - не автоматизировано
         """
    )
    def test_create_contest_dates_validate(self):
        with allure.step("Подготовить данные для нового конкурса без полей с датами"):
            dates = None

        with allure.step("Отправить запрос на создание без поля dates"):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с полями дат в неверном формате"):
            dates = {
                "start": (datetime.today() + timedelta(1)).strftime("%m-%Y-%dT00:00"),
                # изменен порядок следования год и месяца
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%d"
                ),  # нет минут и секунд
                "finish": (datetime.today() + timedelta(20)).strftime("%Y %m %dT00:00"),
                # разделитель не тире, а пробел
            }

        with allure.step("Отправить запрос на создание конкурса с полями дат в неверном формате"):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата начала меньше текущей"
        ):
            dates = {
                "start": (datetime.today() - timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }
        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата начала меньше текущей"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата начала в текущий день но по времени больше настоящего"
        ):
            dates = {
                "start": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата начала в текущий день но по времени больше настоящего"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс  был создан успешно, ответ 201"):
            assert create_contest_response.status_code == 201

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата начала больше даты окончания приема работ"
        ):
            dates = {
                "start": (datetime.now() + timedelta(15)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата начала больше даты окончания приема работ"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс  не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата начала больше даты окончания конкурса"
        ):
            dates = {
                "start": (datetime.now() + timedelta(30)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата начала больше даты окончания конкурса"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс  не был создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата окончания приема работа полностью равна дате окончания конкурса"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.today() + timedelta(10)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата окончания приема работа полностью равна дате окончания конкурса"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс был создан успешно, ответ 201"):
            assert create_contest_response.status_code == 201

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата приема работ больше даты окончания по минутам"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (
                    datetime.today() + timedelta(days=10, minutes=30)
                ).strftime("%Y-%m-%dT%H:%M"),
                "finish": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата приема работ больше даты окончания по минутам"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс был не создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Подготовить данные для нового конкурса с полями дат где дата окончания между датами начала и приема работ"
        ):
            dates = {
                "start": (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                "endOfAcceptanceOfWork": (datetime.now() + timedelta(20)).strftime(
                    "%Y-%m-%dT00:00"
                ),
                "finish": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
            }

        with allure.step(
            "Отправить запрос на создание конкурса с полями дат где дата окончания между датами начала и приема работ"
        ):
            create_contest_response = self.api_contests.create(dates=dates)

        with allure.step("Проверить, что конкурс был не создан успешно, ответ 422"):
            assert create_contest_response.status_code == 422

    @allure.id("2626")
    @allure.title("Создание конкурса: валидация изображений")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что: 
        - поля c изображениями обязательные при создании конкурса
        - - принимаются форматы jpg, jpeg, png, heic, heif (в тесте проверяется только формат jpg, так как png используется в дефолтном создании)
        """
    )
    def test_create_contest_images_validate(self):
        with allure.step("Подготовить данные для нового конкурса без изображений"):
            images = None

        with allure.step("Создаем конкурс без изображений"):
            create_contest_response = self.api_contests.create(images=images)

        with allure.step("Проверяем, что конкурс не был успешно создан"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с изображениями в формате jpg"):
            images = utils_cocreate.set_contest_images(
                desktop="contest-desktop-jpg.jpg",
                mobile="contest-mobile-jpg.jpg",
                main="contest-main-jpg.jpg",
            )

        with allure.step("Создаем конкурс с изображениями в формате jpg"):
            create_contest_response = self.api_contests.create(images=images)

        with allure.step("Проверяем, что конкурс был успешно создан"):
            assert create_contest_response.status_code == 201

    @allure.id("2627")
    @allure.title("Создание конкурса: валидация правил")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что: 
        - файл с правилами обязательный при создании конкурса
        - можно загрузить файлы формата pdf, doc, docx (в тесте проверяется только форматы doc, docx, так как pdf используется в дефолтном создании)
        """
    )
    def test_create_contest_rules_validate(self):
        with allure.step("Подготовить данные для нового конкурса без файла с правилами"):
            rules = None

        with allure.step("Создать конкурс без файла с правилами"):
            create_contest_response = self.api_contests.create(rules=rules)

        with allure.step("Проверить, что конкурс не был успешно создан"):
            assert create_contest_response.status_code == 422

        with allure.step("Подготовить данные для нового конкурса с файлом правил в формате doc"):
            rules = utils_cocreate.set_contest_rules(rules="rules-doc.doc")

        with allure.step("Создать конкурс с файлом правил в формате doc"):
            create_contest_response = self.api_contests.create(rules=rules)

        with allure.step("Проверить, что конкурс был успешно создан"):
            assert create_contest_response.status_code == 201

        with allure.step("Подготовить данные для нового конкурса с файлом правил в формате docx"):
            rules = utils_cocreate.set_contest_rules(rules="rules-docx.docx")

        with allure.step("Создать конкурс с файлом правил в формате docx"):
            create_contest_response = self.api_contests.create(rules=rules)

        with allure.step("Проверить, что конкурс был успешно создан"):
            assert create_contest_response.status_code == 201

    @allure.id("2629")
    @allure.title("Создание конкурса: валидация видимости")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что: 
        - поле обязательное - без него конкурс не создается
        - 1: создается активным
        - 0: создается не активным
    """
    )
    def test_create_contest_visibility_validate(self):
        with allure.step("Отправить запрос на создание конкурса без параметра visible"):
            create_contest_response = self.api_contests.create(visible=None)

        with allure.step("Проверить, что статус запроса 422"):
            assert create_contest_response.status_code == 422

        with allure.step("Отправить запрос на создание конкурса с параметром visible=1"):
            create_contest_response = self.api_contests.create(visible=1)

        with allure.step("Проверить, что статус запроса 201. У конкурса видимость True"):
            assert create_contest_response.status_code == 201
            assert create_contest_response.json()["data"]["visible"] == True

        with allure.step("Отправить запрос на создание конкурса с параметром visible=0"):
            create_contest_response = self.api_contests.create(visible=0)

        with allure.step("Проверить, что статус запроса 201. У конкурса видимость False"):
            assert create_contest_response.status_code == 201
            assert create_contest_response.json()["data"]["visible"] == False

    @allure.id("2630")
    @allure.title("Создание конкурса: валидация вывода на главной")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка конкурса")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Contests")
    @allure.description(
        """Проверяем, что: 
        - поле обязательное - без него конкурс не создается
        - 1: создается активным
        - 0: создается не активным
    """
    )
    def test_create_contest_show_on_main_validate(self):
        with allure.step("Отправить запрос на создание конкурса без параметра isVisibleOnMainPage"):
            create_contest_response = self.api_contests.create(isVisibleOnMainPage=None)

        with allure.step("Проверить, что статус запроса 422"):
            assert create_contest_response.status_code == 422

        with allure.step(
            "Отправить запрос на создание конкурса с параметром isVisibleOnMainPage=1"
        ):
            create_contest_response = self.api_contests.create(isVisibleOnMainPage=1)
            contest_on_main_id = create_contest_response.json()["data"]["id"]

        with allure.step("Проверить, что статус запроса 201. У конкурса вывод на главной True"):
            assert create_contest_response.status_code == 201
            assert create_contest_response.json()["data"]["isVisibleOnMainPage"] == True

        with allure.step(
            "Отправить запрос на создание конкурса с параметром isVisibleOnMainPage=0"
        ):
            create_contest_response = self.api_contests.create(isVisibleOnMainPage=0)

        with allure.step("Проверить, что статус запроса 201. У конкурса вывод на главной False"):
            assert create_contest_response.status_code == 201
            assert create_contest_response.json()["data"]["isVisibleOnMainPage"] == False

        with allure.step(
            "Отправить запрос на создание еще одного конкурса с параметром isVisibleOnMainPage=1"
        ):
            create_contest_response = self.api_contests.create(isVisibleOnMainPage=1)

        with allure.step(
            """Проверить, что статус запроса 201. У конкурса вывод на главной False. 
            Приходит уведомление, что у другого конкурса признак вывода на главной снят. У другого конкурса признак меняется на False"""
        ):
            assert create_contest_response.status_code == 201
            assert (
                "скрыт с главной страницы" in create_contest_response.json()["alerts"][1]["text"]
                and f"{contest_on_main_id}" in create_contest_response.json()["alerts"][1]["text"]
            )
            assert (
                self.api_contests.get_one(contest_id=contest_on_main_id).json()["data"][
                    "isVisibleOnMainPage"
                ]
                == 0
            )
