import allure

from pytest_voluptuous import S
from allure_commons.types import Severity
from befree.api_model.config.internal import ConfigInternal
from befree.api_model.config.public import ConfigPublic
from befree.api_model.config.private import ConfigPrivate
from befree.api_model.config.db_queries.queries import QueriesConfig
from befree.api_model.config.internal.default import shemas as shemas_internal
from befree.api_model.config import utils as utils_config


class TestConfig(ConfigInternal, ConfigPublic, ConfigPrivate, QueriesConfig):
    @allure.id("2687")
    @allure.title("Получение списка настроек интернал конфига")
    @allure.label("service", "Config")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем получение списка настроек интернал методом")
    def test_internal_config(self):
        with allure.step("Отправить запрос с пустым массивом ключей"):
            configs_response = self.api_internal_config.get()
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные пришли"):
                assert configs_response.json()["configs"]

        with allure.step("Отправить запрос с несуществующим ключом"):
            configs_response = self.api_internal_config.get(keys=["qwerty"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные не пришли"):
                assert configs_response.json()["configs"] == None

        with allure.step("Отправить запрос с приватному ключу"):
            configs_response = self.api_internal_config.get(keys=["inventory_rn_limit"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.private_config)

        with allure.step("Отправить запрос по ключу с типом int"):
            configs_response = self.api_internal_config.get(keys=["freeShippingSum"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.int_config)

        with allure.step("Отправить запрос по ключу с типом str"):
            configs_response = self.api_internal_config.get(keys=["mobile_version_ios"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.str_config)

        with allure.step("Отправить запрос по ключу с типом root"):
            configs_response = self.api_internal_config.get(keys=["paymentPickupPoint", "paymentOMNI"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.root_config)

    @allure.id("2682")
    @allure.title("Получение списка настроек публичного конфига")
    @allure.label("service", "Config")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем получение списка настроек публичным методом")
    def test_public_config(self):
        with allure.step("Отправить запрос с пустым массивом ключей"):
            configs_response = self.api_public_config.get()
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные пришли"):
                assert configs_response.json()["configs"]

        with allure.step("Отправить запрос с несуществующим ключом"):
            configs_response = self.api_public_config.get(keys=["qwerty"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные не пришли"):
                assert configs_response.json()["configs"] == None

        with allure.step("Отправить запрос с приватному ключу"):
            configs_response = self.api_public_config.get(keys=["inventory_rn_limit"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные не пришли"):
                assert configs_response.json()["configs"] == None

        with allure.step("Отправить запрос по ключу с типом int"):
            configs_response = self.api_public_config.get(keys=["freeShippingSum"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.int_config)

        with allure.step("Отправить запрос по ключу с типом str"):
            configs_response = self.api_public_config.get(keys=["mobile_version_ios"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.str_config)

        with allure.step("Отправить запрос по ключу с типом root"):
            configs_response = self.api_public_config.get(keys=["paymentPickupPoint", "paymentOMNI"])
            assert configs_response.status_code == 200

            with allure.step("Проверяем, что данные соответствуют схеме"):
                assert configs_response.json() == S(shemas_internal.root_config)

    @allure.id("2686")
    @allure.title("Получение списка настроек интернал конфига")
    @allure.label("service", "Config")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("CMS")
    @allure.description("Проверяем получение списка настроек интернал методом")
    def test_private_config(self):
        with allure.step("Отправить запрос с пустым массивом ключей"):
            configs_response = self.api_private_config.update()
            assert configs_response.status_code == 204

        with allure.step("Отправить запрос на изменение ключа с типом int"):
            key = "freeShippingSum"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи"):
                value = config_bd[0]["value_int"] + 1
                configs_response = self.api_private_config.update_single(title=config_bd[0]["title"], key=key, value=value)
                assert configs_response.status_code == 204

            with allure.step("Проверяем, что значение в бд изменилось"):
                config_bd = self.get_config_by_key(key=key)
                assert config_bd[0]["value_int"] == value

        with allure.step("Отправить запрос на изменение ключа с типом str"):
            key = "mobile_version_ios"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи"):
                value = "8.7.1a"
                configs_response = self.api_private_config.update_single(title=config_bd[0]["title"], key=key, value=value)
                assert configs_response.status_code == 204

            with allure.step("Проверяем, что значение в бд изменилось"):
                config_bd = self.get_config_by_key(key=key)
                assert config_bd[0]["value_string"] == value

        with allure.step("Отправить запрос на изменение ключа с типом bool"):
            key = "captcha"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи"):
                value = False if config_bd[0]["value_bool"] else True

                configs_response = self.api_private_config.update_single(title=config_bd[0]["title"], key=key, value=value)
                assert configs_response.status_code == 204

            with allure.step("Проверяем, что значение в бд изменилось"):
                config_bd = self.get_config_by_key(key=key)
                assert config_bd[0]["value_bool"] == value

        with allure.step("Отправить запрос на изменение ключа с типом root"):
            key = "paymentOMNI2"

            with allure.step("Получаем значение всех настроек в бд"):
                config_root = self.get_config_by_key(key=key)
                configs_bd = self.get_root_config_by_key(key=key)

            with allure.step("Изменяем значение по ключу через апи"):
                value = False if configs_bd[0]["value_bool"] else True
                root = {"key": key, "title": config_root[0]["title"]}
                configs = utils_config.prepare_configs(configs_bd=configs_bd, value=value)

                configs_response = self.api_private_config.update_root(root=root, configs=configs)
                assert configs_response.status_code == 204

            with allure.step("Проверяем, что значение в бд изменилось"):
                config_root = self.get_root_config_by_key(key=key)
                value_bd = [item["value_bool"] for item in config_root]
                assert all(item == value for item in value_bd)

            with allure.step("Изменяем значение настроек обратно"):
                value = False if value else True
                root = {"key": key, "title": config_root[0]["title"]}
                configs = utils_config.prepare_configs(configs_bd=configs_bd, value=value)

                configs_response = self.api_private_config.update_root(root=root, configs=configs)
                assert configs_response.status_code == 204

            with allure.step("Проверяем, что значение в бд изменилось"):
                config_root = self.get_root_config_by_key(key=key)
                value_bd = [item["value_bool"] for item in config_root]
                assert all(item == value for item in value_bd)

        with allure.step("Отправить запрос на изменение metadata ключа"):
            key = "sticker_new_ttl"

            with allure.step("Получаем значение настройки в бд"):
                config_bd = self.get_config_by_key(key=key)

            with allure.step("Изменяем метадату по ключу через апи"):
                unit = config_bd[0]["metadata"]["unit"] + "1"
                metadata = {"unit": unit}
                configs_response = self.api_private_config.update_single(
                    title=config_bd[0]["title"], key=key, value=config_bd[0]["value_int"], metadata=metadata
                )
                assert configs_response.status_code == 204

            with allure.step("Проверяем, что значение в бд изменилось"):
                config_bd = self.get_config_by_key(key=key)
                assert config_bd[0]["metadata"] == metadata

            with allure.step("Проверяем, что в публичном методе приходит метадата"):
                configs_response = self.api_public_config.get(keys=[key])
                assert configs_response.status_code == 200

                assert configs_response.json()["configs"][0]["metadata"] == metadata
