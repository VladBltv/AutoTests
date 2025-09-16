from mimesis import Person
from befree.api_model.cocreate.public import CocreatePublic
from befree.api_model.customer import Customer
import allure
from allure_commons.types import Severity
from befree.api_model import db_connection


class TestUserAuth(CocreatePublic):
    @allure.id("2681")
    @allure.title("Валидация полей в ЭП авторизации")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.feature("Карточка пользователя")
    @allure.description("""Проверяем, что нельзя авторизоваться при отправке невалидных даных""")
    def test_validate_auth_data(self):
        with allure.step("Авторизоваться под рандомными несуществующими данными"):
            user_login_response = self.api_users_pub.login(
                email=Person().email(), password=Person().password()
            )

        with allure.step("Проверяем, что в ответе статус 401"):
            assert user_login_response.status_code == 401

        with allure.step("Авторизоваться без поля password"):
            user_login_response = self.api_users_pub.login(email=Person().email(), password=None)

        with allure.step("Проверяем, что в ответе статус 422 и сообщение Поле пароль обязательно."):
            assert user_login_response.status_code == 422
            assert "Поле пароль обязательно" in str(user_login_response.json())

        with allure.step("Авторизоваться без поля email"):
            user_login_response = self.api_users_pub.login(email=None, password=Person().password())

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Поле email адрес обязательно"
        ):
            assert user_login_response.status_code == 422
            assert "Поле email адрес обязательно" in str(user_login_response.json())

        with allure.step("Авторизоваться без передачи поля mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru", password="aA123456", mindBox=None
            )

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Поле MindBox обязательно и Поле идентификатор запроса обязательно"
        ):
            assert user_login_response.status_code == 422
            assert "Поле MindBox обязательно" in str(user_login_response.json())
            assert "Поле идентификатор запроса обязательно" in str(user_login_response.json())

        with allure.step("Авторизоваться с пустым полем mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru", password="aA123456", mindBox={}
            )

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Поле MindBox обязательно и Поле идентификатор запроса обязательно"
        ):
            assert user_login_response.status_code == 422
            assert "Поле MindBox обязательно" in str(user_login_response.json())
            assert "Поле идентификатор запроса обязательно" in str(user_login_response.json())

        with allure.step("Авторизоваться с без поля endpointId в mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru",
                password="aA123456",
                mindBox={"deviceUuid": "fd399d03-24ba-43cc-a3e6-b23f34c4c944"},
            )

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Поле идентификатор запроса обязательно"
        ):
            assert user_login_response.status_code == 422
            assert "Поле идентификатор запроса обязательно" in str(user_login_response.json())

        with allure.step("Авторизоваться с пустым полем endpointId в mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru",
                password="aA123456",
                mindBox={"endpointId": "", "deviceUuid": "fd399d03-24ba-43cc-a3e6-b23f34c4c944"},
            )

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Поле идентификатор запроса обязательно"
        ):
            assert user_login_response.status_code == 422
            assert "Поле идентификатор запроса обязательно" in str(user_login_response.json())

        with allure.step("Авторизоваться с произвольным значением endpointId в mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru",
                password="aA123456",
                mindBox={
                    "endpointId": "random",
                    "deviceUuid": "fd399d03-24ba-43cc-a3e6-b23f34c4c944",
                },
            )

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Выбранное значение для mind box.endpoint id ошибочно"
        ):
            assert user_login_response.status_code == 422
            assert "Выбранное значение для mind box.endpoint id ошибочно" in str(
                user_login_response.json()
            )

        with allure.step("Авторизоваться без поля deviceUuid в mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru",
                password="aA123456",
                mindBox={"endpointId": "Befree.Cocreate"},
            )

        with allure.step("Проверяем, что в ответе статус 200"):
            assert user_login_response.status_code == 200

        with allure.step("Авторизоваться с пустым полем deviceUuid в mindbox"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru",
                password="aA123456",
                mindBox={"endpointId": "Befree.Cocreate", "deviceUuid": ""},
            )

        with allure.step("Проверяем, что в ответе статус 200"):
            assert user_login_response.status_code == 200

        with allure.step("Авторизоваться с полем deviceUuid в mindbox в неверном формате"):
            user_login_response = self.api_users_pub.login(
                email="sunny208@yandex.ru",
                password="aA123456",
                mindBox={"endpointId": "Befree.Cocreate", "deviceUuid": "23456789"},
            )

        with allure.step(
            "Проверяем, что в ответе статус 422 и сообщение Значение поля идентификатор устройства должно быть корректным UUID"
        ):
            assert user_login_response.status_code == 422
            assert "Значение поля идентификатор устройства должно быть корректным UUID" in str(
                user_login_response.json()
            )

    @allure.id("2680")
    @allure.title("Создание пользователя через авторизацию")
    @allure.label("service", "Cocreate")
    @allure.label("owner", "potegovaav")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Account")
    @allure.feature("Карточка пользователя")
    @allure.description(
        """Если залогиниться в кокре, под юзером который есть в монолите, но нет в кокре, то в кокре создается пользователь"""
    )
    def test_create_user_via_login(self):
        with allure.step("Зарегистрировать нового пользователя в монолите"):
            email = Person().email()
            password = "aA123456"
            customer = Customer(email=email, password=password)
            register_customer_response = customer.register()
            token = register_customer_response.json()["token"]
            get_customer_response = customer.get_customer(token=token)
            customer_id = get_customer_response.json()["id"]

        with allure.step("Проверить, что в базе кокра нет нового пользователя"):
            query = f"""
                select u.id, u.customer_id, u.email
                from users u
                where u.email = '{email}' and u.customer_id = {customer_id}
            """

            user_base = db_connection.cocreate.get_data(query)

            assert len(user_base) == 0

        with allure.step("Авторизоваться под новым пользователем в кокре"):
            self.api_users_pub.login(email=email, password=password)

        with allure.step("Проверить, что в базе кокра появился этот пользователь"):
            user_base = db_connection.cocreate.get_data(query)
            assert len(user_base) == 1
            assert user_base[0]["email"] == email
            assert user_base[0]["customer_id"] == customer_id
