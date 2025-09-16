from befree.api_model.cocreate.public import CocreatePublic
import allure
from allure_commons.types import Severity
from utils import helpers


class TestUserAccount(CocreatePublic):
    @allure.id("2678")
    @allure.title("Удаление аватара пользователя")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.feature("Карточка пользователя")
    @allure.description("""Проверяем удаление аватара у пользователя""")
    def test_delete_user_avatar(self):
        with allure.step("Попробовать удалить аватар из под неавторизованного пользователя"):
            delete_avatar_response = self.api_users_pub.delete_avatar()

        with allure.step("Проверить, что метод отдает 401 статус"):
            assert delete_avatar_response.status_code == 401

        with allure.step("Попробовать удалить аватар из под невалидного токена"):
            delete_avatar_response = self.api_users_pub.delete_avatar(
                token=helpers.random_bearer_token()
            )

        with allure.step("Проверить, что метод отдает 401 статус"):
            assert delete_avatar_response.status_code == 401

        with allure.step("Авторизоваться под существующим пользователем"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru", password="aA123456"
            )
            token = user_login_response.json()["data"]["token"]
            user_id = user_login_response.json()["data"]["id"]

        with allure.step("Загрузить аватар"):
            set_avatar_response = self.api_users_pub.update_avatar(token=token)
            get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

        with allure.step("Проверить, что аватар установлен"):
            assert len(set_avatar_response.json()["data"]["photo"]) > 0
            assert len(get_user_response.json()["data"]["photo"]) > 0

        with allure.step("Удалить аватар"):
            delete_avatar_response = self.api_users_pub.delete_avatar(token=token)
            get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

        with allure.step("Проверить, что аватара больше нет"):
            assert delete_avatar_response.status_code == 200
            assert get_user_response.json()["data"]["photo"] == None

    @allure.id("2679")
    @allure.title("Обновление аватара пользователя")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.feature("Карточка пользователя")
    @allure.description("""Проверяем обновление аватара у пользователя""")
    def test_update_user_avatar(self):
        with allure.step("Попробовать обновить аватар из под неавторизованного пользователя"):
            update_avatar_response = self.api_users_pub.update_avatar()

        with allure.step("Проверить, что статус код ответа 401"):
            assert update_avatar_response.status_code == 401

        with allure.step("Попробовать обновить аватар из под невалидного токена"):
            update_avatar_response = self.api_users_pub.update_avatar(
                token=helpers.random_bearer_token()
            )

        with allure.step("Проверить, что статус код ответа 401"):
            assert update_avatar_response.status_code == 401

        with allure.step("Загрузка аватара под авторизованным пользователем"):
            with allure.step("Авторизоваться под существующим пользователем"):
                user_login_response = self.api_users_pub.login(
                    email="sunny208@yandex.ru", password="aA123456"
                )
                token = user_login_response.json()["data"]["token"]
                user_id = user_login_response.json()["data"]["id"]

            with allure.step("Можно загрузить аватар в формате png"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Загрузить файл в формате png"):
                    set_avatar_response = self.api_users_pub.update_avatar(
                        token=token, avatar="avatar-png.png"
                    )
                    get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

                with allure.step("Проверить, что ответ 201"):
                    assert set_avatar_response.status_code == 201

                with allure.step("Проверить, что аватар установлен"):
                    assert len(set_avatar_response.json()["data"]["photo"]) > 0
                    assert len(get_user_response.json()["data"]["photo"]) > 0

            with allure.step("Можно загрузить аватар в формате jpeg"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Загрузить файл в формате jpeg"):
                    set_avatar_response = self.api_users_pub.update_avatar(
                        token=token, avatar="avatar-jpeg.jpeg"
                    )
                    get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

                with allure.step("Проверить, что ответ 201"):
                    assert set_avatar_response.status_code == 201

                with allure.step("Проверить, что аватар установлен"):
                    assert len(set_avatar_response.json()["data"]["photo"]) > 0
                    assert len(get_user_response.json()["data"]["photo"]) > 0

            with allure.step("Можно загрузить аватар в формате jpg"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Загрузить файл в формате jpg"):
                    set_avatar_response = self.api_users_pub.update_avatar(
                        token=token, avatar="collab-desktop-jpg.jpg"
                    )
                    get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

                with allure.step("Проверить, что ответ 201"):
                    assert set_avatar_response.status_code == 201

                with allure.step("Проверить, что аватар установлен"):
                    assert len(set_avatar_response.json()["data"]["photo"]) > 0
                    assert len(get_user_response.json()["data"]["photo"]) > 0

            with allure.step("Можно загрузить аватар в формате webp"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Загрузить файл в формате webp"):
                    set_avatar_response = self.api_users_pub.update_avatar(
                        token=token, avatar="avatar-webp.webp"
                    )
                    get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

                with allure.step("Проверить, что ответ 201"):
                    assert set_avatar_response.status_code == 201

                with allure.step("Проверить, что аватар установлен"):
                    assert len(set_avatar_response.json()["data"]["photo"]) > 0
                    assert len(get_user_response.json()["data"]["photo"]) > 0

            with allure.step("Нельзя загрузить аватар в формате gif"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Загрузить файл в формате gif"):
                    set_avatar_response = self.api_users_pub.update_avatar(
                        token=token, avatar="gif-image.gif"
                    )
                    get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

                with allure.step("Проверить, что ответ не 201"):
                    assert set_avatar_response.status_code != 201

                with allure.step("Проверить, что аватар не установлен"):
                    assert get_user_response.json()["data"]["photo"] == None

            with allure.step("Нельзя загрузить аватар в формате doc"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Загрузить файл в формате doc"):
                    set_avatar_response = self.api_users_pub.update_avatar(
                        token=token, avatar="rules-doc.doc"
                    )
                    get_user_response = self.api_users_pub.get_one(user_id=user_id, token=token)

                with allure.step("Проверить, что ответ не 201"):
                    assert set_avatar_response.status_code != 201

                with allure.step("Проверить, что аватар не установлен"):
                    assert get_user_response.json()["data"]["photo"] == None

            with allure.step("Нельзя отправить пустое поле с аватаром"):
                with allure.step("Очистить аватар"):
                    self.api_users_pub.delete_avatar(token=token)

                with allure.step("Передать в поле avatar None"):
                    set_avatar_response = self.api_users_pub.update_avatar(token=token, avatar=None)

                with allure.step("Проверить, что ответ 422, ошибка Поле фотография обязательно"):
                    assert set_avatar_response.status_code == 422
                    assert "Поле фотография обязательно" in str(set_avatar_response.json())
