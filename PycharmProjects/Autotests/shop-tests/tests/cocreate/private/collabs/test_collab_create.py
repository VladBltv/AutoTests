import allure
from allure_commons.types import Severity
from befree.api_model import db_connection

from befree.api_model.cocreate.private import CocreatePrivate
from befree.api_model.cocreate import utils as utils_cocreate


class TestCollabCreate(CocreatePrivate):
    @allure.id("2585")
    @allure.title("Создание коллаборации: валидация поля title")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что нельзя создать коллаборацию без поля title и с данными длинной более 255 символов"""
    )
    def test_create_collaboration_title_validate(self):
        with allure.step("Подготовить данные для новой коллаборации без поля title"):
            title = None

        with allure.step("Создаем коллаборацию без title"):
            create_collaboration_response = self.api_collaborations.create(title=title)

        with allure.step("Проверяем, что коллаборация не создалась, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для новой коллаборации c полем title длиннее 255 символов"
        ):
            title = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и форм"

        with allure.step("Создаем коллаборацию c полем title длиннее 255 символов"):
            create_collaboration_response = self.api_collaborations.create(title=title)

        with allure.step("Проверяем, что коллаборация не создалась, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для новой коллаборации c полем title ровно 255 символов"
        ):
            title = (
                "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и фор",
            )

        with allure.step("Создаем коллаборацию c полем title ровно 255 символов"):
            create_collaboration_response = self.api_collaborations.create(title=title)

        with allure.step("Проверяем, что коллаборация создалась, ответ 201"):
            assert create_collaboration_response.status_code == 201

    @allure.id("2586")
    @allure.title("Создание коллаборации: валидация поля description")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что можно создать коллаборацию без поля description, нельзя создать с данными длинной более 255 символов"""
    )
    def test_create_collaboration_description_validate(self):
        with allure.step("Подготовить данные для новой коллаборации без поля description"):
            description = None

        with allure.step("Создаем коллаборацию без поля description"):
            create_collaboration_response = self.api_collaborations.create(description=description)

        with allure.step("Проверяем, что коллаборация создалась, ответ 201"):
            assert create_collaboration_response.status_code == 201

        with allure.step(
            "Подготовить данные для новой коллаборации c полем description длиннее 255 символов"
        ):
            description = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и форм"

        with allure.step("Создаем коллаборацию c полем description длиннее 255 символов"):
            create_collaboration_response = self.api_collaborations.create(description=description)

        with allure.step("Проверяем, что коллаборация не создалась, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для новой коллаборации c полем description ровно 255 символов"
        ):
            description = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и фор"

        with allure.step("Создаем коллаборацию c полем description ровно 255 символов"):
            create_collaboration_response = self.api_collaborations.create(description=description)

        with allure.step("Проверяем, что коллаборация создалась, ответ 201"):
            assert create_collaboration_response.status_code == 201

    @allure.id("2587")
    @allure.title("Создание коллаборации: валидация поля landingLink")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что нельзя создать коллаборацию без поля landingLink или если данные в нем неверного формата"""
    )
    def test_create_collaboration_link_validate(self):
        with allure.step("Подготовить данные для новой коллаборации без поля landingLink"):
            landing_link = None

        with allure.step("Создаем коллаборацию без ссылки"):
            create_collaboration_response = self.api_collaborations.create(landingLink=landing_link)

        with allure.step("Проверяем, что коллаборация не была создана, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для новой коллаборации с полем landingLink неверного формата"
        ):
            landing_link = "some/wrong/link"

        with allure.step("Создаем коллаборацию со ссылкой неверного формата"):
            create_collaboration_response = self.api_collaborations.create(landingLink=landing_link)

        with allure.step("Проверяем, что коллаборация не была создана, ответ 422"):
            assert create_collaboration_response.status_code == 422

    @allure.id("2588")
    @allure.title("Создание коллаборации: валидация поля displayType")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что коллаборацию нельзя создать без поля displayType.
    Если значение withoutProducts, то заполнение compilationId не требуется.
    Если значение withProducts, то заполнение compilationId обязательно."""
    )
    def test_create_collaboration_display_type_validate(self):
        with allure.step("Подготовить данные для новой коллаборации без поля displayType"):
            display_type = None

        with allure.step("Создаем коллаборацию без поля displayType"):
            create_collaboration_response = self.api_collaborations.create(displayType=display_type)

        with allure.step("Проверяем, что коллаборация не была создана, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для новой коллаборации с полем displayType=withProducts и без compilationId"
        ):
            display_type = "withProducts"

        with allure.step(
            "Создаем коллаборацию с полем displayType=withProducts и без compilationId"
        ):
            create_collaboration_response = self.api_collaborations.create(displayType=display_type)

        with allure.step("Проверяем, что коллаборация не была успешно создана, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для новой коллаборации с полем displayType=withoutProducts и без compilationId"
        ):
            ...

        with allure.step(
            "Создаем коллаборацию с полем displayType=withoutProducts и без compilationId"
        ):
            create_collaboration_response = self.api_collaborations.create()

        with allure.step("Проверяем, что коллаборация была успешно создана, ответ 201"):
            assert create_collaboration_response.status_code == 201

        with allure.step(
            "Подготовить данные для новой коллаборации с полем displayType=withProducts и c compilationId"
        ):
            display_type = "withProducts"
            compilation_id = 115

        with allure.step("Создаем коллаборацию с полем displayType=withProducts и compilationId"):
            create_collaboration_response = self.api_collaborations.create(
                displayType=display_type, compilationId=compilation_id
            )

        with allure.step("Проверяем, что коллаборация была успешно создана, ответ 201"):
            assert create_collaboration_response.status_code == 201

        with allure.step(
            "Подготовить данные для новой коллаборации с полем displayType=withoutProducts и c compilationId"
        ):
            compilation_id = 115

        with allure.step(
            "Создаем коллаборацию с полем displayType=withoutProducts и compilationId"
        ):
            create_collaboration_response = self.api_collaborations.create(
                compilationId=compilation_id
            )

        with allure.step("Проверяем, что коллаборация не была успешно создана, ответ 422"):
            assert create_collaboration_response.status_code == 422

    @allure.id("2591")
    @allure.title("Создание коллаборации: валидация поля visible")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("""Проверяем, что нельзя создать коллаборацию без указания поля visible""")
    def test_create_collaboration_visible_validate(self):
        with allure.step("Подготовить данные для новой коллаборации без поля visible"):
            visible = None

        with allure.step("Создаем коллаборацию без поля visible"):
            create_collaboration_response = self.api_collaborations.create(visible=visible)

        with allure.step("Проверяем, что коллаборация не была успешно создана, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step("Подготовить данные для новой коллаборации с полем visible=0"):
            visible = 0

        with allure.step("Создаем коллаборацию с полем visible=0"):
            create_collaboration_response = self.api_collaborations.create(visible=visible)

        with allure.step("Проверяем, что коллаборация успешно создана, в статусе неактивно"):
            assert (
                create_collaboration_response.status_code == 201
                and create_collaboration_response.json()["data"]["visible"] is False
            )

    @allure.id("2590")
    @allure.title("Создание коллаборации: валидация поля userId")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("""Проверяем, что коллаборацию можно создать без пользователя""")
    def test_create_collaboration_user_validate(self):
        with allure.step("Подготовить данные для новой коллаборации без поля userId"):
            user_id = None

        with allure.step("Создаем коллаборацию без поля userId"):
            create_collaboration_response = self.api_collaborations.create(userId=user_id)

        with allure.step("Проверяем, что коллаборация успешно создана"):
            assert create_collaboration_response.status_code == 201

    @allure.id("2589")
    @allure.title("Создание коллаборации: валидация наличия изображений")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что 
    - нельзя создать коллаборацию без изображений
    - можно загрузить форматы png и jpg
    В данном тесте проверяется дополнительно формат jpg, формат png грузится по дефолту
    """
    )
    def test_create_collaboration_without_images(self):
        with allure.step(
            "Подготовить данные для новой коллаборации, только поля с данными без изображений"
        ):
            images = None

        with allure.step("Создаем коллаборацию без изображений"):
            create_collaboration_response = self.api_collaborations.create(images=images)

        with allure.step("Проверяем, что коллаборация не была успешно создана"):
            assert create_collaboration_response.status_code == 422

        with allure.step("Подготовить данные для новой коллаборации с изображениями в формате jpg"):
            images = utils_cocreate.set_collaboration_images(
                desktop="collab-desktop-jpg.jpg", mobile="collab-mobile-jpg.jpg"
            )

        with allure.step("Создаем коллаборацию с изображениями в формате jpg"):
            create_collaboration_response = self.api_collaborations.create(images=images)

        with allure.step("Проверяем, что коллаборация была успешно создана"):
            assert create_collaboration_response.status_code == 201

    @allure.id("2592")
    @allure.title("Создание коллаборации с выводом на главной")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Можно создать только одну коллабрацию с выводом на главной, если до этого уже существовала коллаборация с выводом на главной, 
        то у прежней коллаборации признак убирается. Поле isVisibleOnMainPage обязательно """
    )
    def test_create_collaboration_on_main(self):
        with allure.step("Подготовить данные для создания коллаборации с выводом на главной"):
            on_main = "1"

        with allure.step("Создать коллаборацию с выводом на главной"):
            create_collaboration_response = self.api_collaborations.create(
                isVisibleOnMainPage=on_main
            )

        with allure.step("Проверяем, что новая коллаборация создана успешно"):
            assert create_collaboration_response.status_code == 201

        with allure.step(
            "Проверяем, что у созданной коллаборации установлен соответствующий признак"
        ):
            assert create_collaboration_response.json()["data"]["isVisibleOnMainPage"] is True

        with allure.step("Проверяем, что в базе больше нет коллабораций с таким признаком"):
            query = f"""
                        select c.id 
                        from collaborations c 
                        where c.is_show_main is true and c.deleted_at is null and c.is_visible is true
                    """

            collaborations_base = list(
                map(lambda n: n["id"], db_connection.cocreate.get_data(query))
            )

            assert (
                len(collaborations_base) == 1
                and collaborations_base[0] == create_collaboration_response.json()["data"]["id"]
            )

        with allure.step(
            "Подготовить данные для создания коллаборации без параметра вывода на главной"
        ):
            on_main = None

        with allure.step("Создать коллаборацию без параметра вывода на главной"):
            create_collaboration_response = self.api_collaborations.create(
                isVisibleOnMainPage=on_main
            )

        with allure.step("Проверяем, что новая коллаборация не была создана успешно, ответ 422"):
            assert create_collaboration_response.status_code == 422

    @allure.id("2593")
    @allure.title(
        "При создании в поле type для коллаборации можно передать только значения из определенного списка"
    )
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """В поле type коллаборации обязательно и принимает только определенные значения. Будут реализованы позже, пока заглушки"""
    )
    def test_create_collaboration_type_validate(self):
        with allure.step("Подготовить данные для создания коллаборации без поля type"):
            collab_type = None

        with allure.step("Создать коллаборацию без параметра type"):
            create_collaboration_response = self.api_collaborations.create(type=collab_type)

        with allure.step("Проверяем, что новая коллаборация не была создана успешно, ответ 422"):
            assert create_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для создания коллаборации c полем type с произвольным значением не из разрешенных"
        ):
            collab_type = "somewrongtype"

        with allure.step("Создать коллаборацию с неверным параметром type"):
            create_collaboration_response = self.api_collaborations.create(type=collab_type)

        with allure.step("Проверяем, что новая коллаборация не была создана успешно, ответ 422"):
            assert create_collaboration_response.status_code == 422
