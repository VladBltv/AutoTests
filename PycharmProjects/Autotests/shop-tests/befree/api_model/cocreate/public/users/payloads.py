import json
from utils import helpers
from befree.api_model.cocreate import utils
from befree.api_model.cocreate.public.users.schemas import update_user_request_schema
from mimesis import Person


class Payloads:
    def login(self, **kwargs):
        payload = {}

        if "email" in kwargs:
            if kwargs["email"] is not None:
                payload["email"] = kwargs.pop("email")
        else:
            payload["email"] = Person().email()

        if "password" in kwargs:
            if kwargs["password"] is not None:
                payload["password"] = kwargs.pop("password")
        else:
            payload["email"] = Person().password()

        if "mindBox" in kwargs:
            if kwargs["mindBox"] is not None:
                payload["mindBox"] = kwargs.pop("mindBox")
        else:
            payload["mindBox"] = {
                "endpointId": "Befree.Cocreate",
                "deviceUuid": "fd399d03-24ba-43cc-a3e6-b23f34c4c944",
            }

        return json.dumps(payload)

    def update_user(self, current_data, **kwargs):
        schema = update_user_request_schema
        payload = helpers.get_payload_for_update(current_data=current_data, schema=schema, **kwargs)

        return json.dumps(payload)

    def set_avatar(self, **kwargs):
        files = {}

        if "avatar" in kwargs:
            if kwargs["avatar"] is not None:
                files = utils.set_avatar_image(avatar=kwargs.pop("avatar"))
        else:
            files = utils.set_avatar_image()

        return files

    def check_code(self, **kwargs):
        payload = {}

        if "code" in kwargs:
            if kwargs["code"] is not None:
                payload["code"] = kwargs.pop("code")
        else:
            payload["code"] = 12345

        return json.dumps(payload)

    def get_code(self, **kwargs):
        payload = {}

        if "verificationPhone" in kwargs:
            if kwargs["verificationPhone"] is not None:
                payload["verificationPhone"] = kwargs.pop("verificationPhone")
        else:
            payload["verificationPhone"] = Person().phone_number(mask="+7 (###) ###-##-##")

        return json.dumps(payload)

    def register(self, **kwargs):
        payload = {}

        if "email" in kwargs:
            if kwargs["email"] is not None:
                payload["email"] = kwargs.pop("email")
        else:
            payload["email"] = Person().email()

        if "firstName" in kwargs:
            if kwargs["firstName"] is not None:
                payload["firstName"] = kwargs.pop("firstName")
        else:
            payload["firstName"] = Person().first_name()

        if "lastName" in kwargs:
            if kwargs["lastName"] is not None:
                payload["lastName"] = kwargs.pop("lastName")
        else:
            payload["lastName"] = Person().last_name()

        if "gender" in kwargs:
            if kwargs["gender"] is not None:
                payload["gender"] = kwargs.pop("gender")
        else:
            payload["gender"] = "female"

        if "birthdayAt" in kwargs:
            if kwargs["birthdayAt"] is not None:
                payload["birthdayAt"] = kwargs.pop("birthdayAt")
        else:
            payload["birthdayAt"] = helpers.random_birth_date()

        if "password" in kwargs:
            if kwargs["password"] is not None:
                payload["password"] = kwargs.pop("password")
        else:
            payload["password"] = Person().password()

        if "passwordConfirmation" in kwargs:
            if kwargs["passwordConfirmation"] is not None:
                payload["passwordConfirmation"] = kwargs.pop("passwordConfirmation")
        else:
            payload["passwordConfirmation"] = Person().password()

        if "phone" in kwargs:
            if kwargs["phone"] is not None:
                payload["phone"] = kwargs.pop("phone")
        else:
            payload["phone"] = Person().phone_number(mask="+7 (###) ###-##-##")

        if "mindBox" in kwargs:
            if kwargs["mindBox"] is not None:
                payload["mindBox"] = kwargs.pop("mindBox")
        else:
            payload["mindBox"] = {
                "deviceUuid": "31bad34a-f4f4-43d6-8e3c-32cfb33e4f77",
                "endpointId": "Befree.Cocreate",
                "subscribe": False,
            }
