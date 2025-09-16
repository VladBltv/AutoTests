import allure
from allure_commons.types import Severity
from mimesis import Text
from befree.api_model.cocreate.private import CocreatePrivate


class TestCollabUpdate(CocreatePrivate):
    @allure.id("2596")
    @allure.title("Нельзя обновить несуществующую или удаленную коллаборацию")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """При обновлении несуществующей или удаленной коллаборации возникает 404 ошибка"""
    )
    def test_update_unexisting_collaboration(self):
        with allure.step("Создать дефолтную коллаборацию для теста"):
            create_collaboration_response = self.api_collaborations.create()
            test_collab_id = create_collaboration_response.json()["data"]["id"]

        with allure.step("Обновить заведомо не существующую коллаборацию"):
            unexisting_collab_id = test_collab_id + 1000
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=unexisting_collab_id
            )

        with allure.step("Проверить, что ответ запроса 404"):
            assert update_collaboration_response.status_code == 404

        with allure.step("Удалить тестовую коллаборацию"):
            self.api_collaborations.delete(collaboration_id=test_collab_id)

        with allure.step("Обновить удаленную коллаборацию"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id
            )

        with allure.step("Проверить, что ответ запроса 404"):
            assert update_collaboration_response.status_code == 404

    @allure.id("2600")
    @allure.title("Ранее установленное описание коллборации можно удалить")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Так как поле описания не обязательное, то при отсутствии данных в поле или отсутствии самого поля 
        при обновлении коллборации удаляет ранее созданные данные"""
    )
    def test_remove_collaboration_description(self):
        with allure.step("Создать дефолтную коллаборацию с описанием"):
            create_collaboration_response = self.api_collaborations.create()
            test_collab_id = create_collaboration_response.json()["data"]["id"]
            assert len(create_collaboration_response.json()["data"]["description"]) > 0

        with allure.step("Обновить данные в коллаборации: в данных отсутствует поле description"):
            get_collaboration_response = self.api_collaborations.get_one(
                collaboration_id=test_collab_id
            )
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id,
                description=None,
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step(
            "Проверить, что коллбаорация обновилаcь успешно и у нее отсутстсвуют данные в поле description"
        ):
            assert (
                update_collaboration_response.status_code == 200
                and update_collaboration_response.json()["data"]["description"] is None
            )

        with allure.step("Обновить данные в коллаборации и восстановить поле description"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id, description=Text("ru").sentence()[:255]
            )
            assert len(update_collaboration_response.json()["data"]["description"]) > 0

        with allure.step(
            "Обновить данные в коллаборации: в данных поле description есть, но с пустыми данными"
        ):
            get_collaboration_response = self.api_collaborations.get_one(
                collaboration_id=test_collab_id
            )
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id,
                description="",
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step(
            "Проверить, что коллбаорация обновилаь успешно и у нее отсутстсвуют данные в поле description"
        ):
            assert (
                update_collaboration_response.status_code == 200
                and update_collaboration_response.json()["data"]["description"] is None
            )

    @allure.id("2598")
    @allure.title("Ранее установленного пользователя у коллборации можно удалить")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Так как поле пользователя не обязательное, то при отсутствии данных в поле или отсутствии самого поля 
        при обновлении коллборации удаляет ранее созданные данные"""
    )
    def test_remove_collaboration_user(self):
        with allure.step("Создать дефолтную коллаборацию с пользователем"):
            create_collaboration_response = self.api_collaborations.create()
            test_collab_id = create_collaboration_response.json()["data"]["id"]
            assert create_collaboration_response.json()["data"]["user"] is not None

        with allure.step("Обновить данные в коллаборации: в данных отсутствует поле user"):
            get_collaboration_response = self.api_collaborations.get_one(
                collaboration_id=test_collab_id
            )
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id,
                userId=None,
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step(
            "Проверить, что коллбаорация обновилаcь успешно и у нее отсутстсвуют данные в поле user"
        ):
            assert (
                update_collaboration_response.status_code == 200
                and update_collaboration_response.json()["data"]["user"] is None
            )

        with allure.step("Обновить данные в коллаборации и восстановить поле user"):
            get_collaboration_response = self.api_collaborations.get_one(
                collaboration_id=test_collab_id
            )
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id,
                userId=252,
                current_data=get_collaboration_response.json()["data"],
            )
            assert update_collaboration_response.json()["data"]["user"] is not None

        with allure.step(
            "Обновить данные в коллаборации: в данных поле user есть, но с пустыми данными"
        ):
            get_collaboration_response = self.api_collaborations.get_one(
                collaboration_id=test_collab_id
            )
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=test_collab_id,
                userId="",
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step(
            "Проверить, что коллбаорация обновилаь успешно и у нее отсутстсвуют данные в поле user"
        ):
            assert (
                update_collaboration_response.status_code == 200
                and update_collaboration_response.json()["data"]["user"] is None
            )

    @allure.id("2601")
    @allure.title(
        "При изменении dysplayType со значения withProducts на значение withoutProducts удаляется привязка к компиляции"
    )
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Если у коллаборации меняется типа с 'с продуктами' на 'без продуктов' то, если поле компиляции отсутствует 
        или содержит пустые данные, запрос успешно отрабатывает и ранее привязанная компиляций отвязывается"""
    )
    def test_display_type_changing_validation(self):
        with allure.step("Создать коллаборацию с dysplayType=withProducts"):
            collaboration_create_response = self.api_collaborations.create(
                displayType="withProducts", compilationId=115
            )
            collab_id = collaboration_create_response.json()["data"]["id"]
            assert collaboration_create_response.json()["data"]["compilation"] is not None

        with allure.step(
            "Обновить коллаборацию на dysplayType=withoutProducts, компиляцию не передаем"
        ):
            get_collaboration_response = self.api_collaborations.get_one(collaboration_id=collab_id)
            collaboration_update_response = self.api_collaborations.update_config(
                collaboration_id=collab_id,
                displayType="withoutProducts",
                compilationId=None,
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step("Проверить, что у коллаборации отвязалась компиляция"):
            assert collaboration_update_response.json()["data"]["compilation"] is None

        with allure.step("Восстановить значение dysplayType=withProducts"):
            get_collaboration_response = self.api_collaborations.get_one(collaboration_id=collab_id)
            self.api_collaborations.update_config(
                collaboration_id=collab_id,
                displayType="withProducts",
                compilationId=115,
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step(
            "Обновить коллаборацию на dysplayType=withoutProducts, в поле компиляции передаем пустые данные"
        ):
            get_collaboration_response = self.api_collaborations.get_one(collaboration_id=collab_id)
            collaboration_update_response = self.api_collaborations.update_config(
                collaboration_id=collab_id,
                displayType="withoutProducts",
                compilationId="",
                current_data=get_collaboration_response.json()["data"],
            )

        with allure.step("Проверить, что у коллаборации отвязалась компиляция"):
            assert collaboration_update_response.json()["data"]["compilation"] is None

    @allure.id("2602")
    @allure.title("Обновление коллаборации: валидация поля title")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что нельзя обновить коллаборацию без поля title и с данными длинной более 255 символов"""
    )
    def test_update_collaboration_title_validate(self):
        with allure.step("Создать дефолтную коллаборацию"):
            create_collaboration_response = self.api_collaborations.create()
            collab_id = create_collaboration_response.json()["data"]["id"]

        with allure.step("Обновить коллаборацию без title"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, title=None
            )

        with allure.step("Проверяем, что коллаборация не обновилась, ответ 422"):
            assert update_collaboration_response.status_code == 422

        with allure.step("Подготовить данные для коллаборации c полем title длиннее 255 символов"):
            title = "Lorem Ipsum - это текст-'рыба', часто используемый в печати и вэб-дизайне. Lorem Ipsum является стандартной 'рыбой' для текстов на латинице с начала XVI или проще говоря 16 века. В то время некий безымянный печатник создал большую коллекцию размеров и форм"

        with allure.step("Обновить коллаборацию c полем title длиннее 255 символов"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, title=title
            )

        with allure.step("Проверить, что коллаборация не обновилась, ответ 422"):
            assert update_collaboration_response.status_code == 422

    @allure.id("2603")
    @allure.title("Обновление коллаборации: валидация поля landingLink")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Проверяем, что нельзя обновить коллаборацию без поля landingLink или если данные в нем неверного формата"""
    )
    def test_update_collaboration_link_validate(self):
        with allure.step("Создать дефолтную коллаборацию"):
            create_collaboration_response = self.api_collaborations.create()
            collab_id = create_collaboration_response.json()["data"]["id"]

        with allure.step("Подготовить данные для коллаборации без поля landingLink"):
            landing_link = None

        with allure.step("Обновить коллаборацию без ссылки"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, landingLink=landing_link
            )

        with allure.step("Проверяем, что коллаборация не была обновлена, ответ 422"):
            assert update_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для коллаборации с полем landingLink неверного формата"
        ):
            landing_link = "some/wrong/link"

        with allure.step("Обновить коллаборацию со ссылкой неверного формата"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, landingLink=landing_link
            )

        with allure.step("Проверяем, что коллаборация не была обновлена, ответ 422"):
            assert update_collaboration_response.status_code == 422

    @allure.id("2604")
    @allure.title("Обновление коллаборации: валидация поля visible")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description("""Проверяем, что нельзя обновить коллаборацию без указания поля visible""")
    def test_update_collaboration_visible_validate(self):
        with allure.step("Создать дефолтную коллаборацию"):
            create_collaboration_response = self.api_collaborations.create()
            collab_id = create_collaboration_response.json()["data"]["id"]

        with allure.step("Подготовить данные для коллаборации без поля visible"):
            visible = None

        with allure.step("Обновить коллаборацию без поля visible"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, visible=visible
            )

        with allure.step("Проверяем, что коллаборация не была успешно создана, ответ 422"):
            assert update_collaboration_response.status_code == 422

        with allure.step("Подготовить данные для коллаборации с полем visible=0"):
            visible = 0

        with allure.step("Обновить коллаборацию с полем visible=0"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, visible=visible
            )

        with allure.step("Проверяем, что коллаборация успешно обновлена, в статусе неактивно"):
            assert (
                update_collaboration_response.status_code == 200
                and update_collaboration_response.json()["data"]["visible"] is False
            )

    @allure.id("2605")
    @allure.title("Обновление коллаборации с выводом на главной")
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """Одномоментно может быть только одна коллаборация с выводом на главной, если до этого уже существовала коллаборация с выводом на главной, 
        то у прежней коллаборации признак убирается. Поле isVisibleOnMainPage обязательно """
    )
    def test_update_collaboration_on_main(self):
        with allure.step("Создать коллаборацию с выводом на главной"):
            create_collaboration_response = self.api_collaborations.create(isVisibleOnMainPage=1)
            collab_id_on_main = create_collaboration_response.json()["data"]["id"]

        with allure.step("Создать коллаборацию без вывода на главной"):
            create_collaboration_response = self.api_collaborations.create(isVisibleOnMainPage=0)
            collab_id_not_on_main = create_collaboration_response.json()["data"]["id"]

        with allure.step(
            "Обновить коллаборацию, которая не была выведена на главной и вывести ее на главно"
        ):
            self.api_collaborations.update_config(
                collaboration_id=collab_id_not_on_main, isVisibleOnMainPage=1
            )

        with allure.step(
            "Проверяем, что у обоих коллабораций признак вывода на главной изменился на противоположный"
        ):
            get_collaboration_response_1 = self.api_collaborations.get_one(
                collaboration_id=collab_id_on_main
            )
            assert get_collaboration_response_1.json()["data"]["isVisibleOnMainPage"] is False

            get_collaboration_response_2 = self.api_collaborations.get_one(
                collaboration_id=collab_id_not_on_main
            )
            assert get_collaboration_response_2.json()["data"]["isVisibleOnMainPage"] is True

        with allure.step(
            "Подготовить данные для создания коллаборации без параметра вывода на главной"
        ):
            on_main = None

        with allure.step("Обновить коллаборацию без параметра вывода на главной"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id_not_on_main, isVisibleOnMainPage=on_main
            )

        with allure.step("Проверяем, что коллаборация не была обновлена успешно, ответ 422"):
            assert update_collaboration_response.status_code == 422

    @allure.id("2606")
    @allure.title(
        "При обновлении в поле type для коллаборации можно передать только значения из определенного списка"
    )
    @allure.label("service", "Cocreate")
    @allure.feature("Карточка коллаборации")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Collabs")
    @allure.description(
        """В поле type коллаборации обязательно и принимает только определенные значения. Будут реализованы позже, пока заглушки"""
    )
    def test_update_collaboration_type_validate(self):
        with allure.step("Создать дефолтную коллаборацию"):
            create_collaboration_response = self.api_collaborations.create()
            collab_id = create_collaboration_response.json()["data"]["id"]

        with allure.step("Обновить коллаборацию без параметра type"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, type=None
            )

        with allure.step("Проверяем, что новая коллаборация не была обновлена успешно, ответ 422"):
            assert update_collaboration_response.status_code == 422

        with allure.step(
            "Подготовить данные для обновления коллаборации c полем type с произвольным значением не из разрешенных"
        ):
            collab_type = "somewrongtype"

        with allure.step("Создать коллаборацию с неверным параметром type"):
            update_collaboration_response = self.api_collaborations.update_config(
                collaboration_id=collab_id, type=collab_type
            )

        with allure.step("Проверяем, что новая коллаборация не была обновлена успешно, ответ 422"):
            assert update_collaboration_response.status_code == 422
