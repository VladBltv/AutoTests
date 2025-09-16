import json


class Payloads:
    def update_settings(self, **kwargs):
        """kwargs should contain current_settings"""
        data = {"items": []}
        existing_settings_list = kwargs.pop("current_settings") if "current_settings" in kwargs else []

        if kwargs:
            for key in kwargs:
                item = {"key": key, "value": kwargs[key]}
                data["items"].append(item)
        else:
            for i in range(0, len(existing_settings_list)):
                item = {
                    "key": existing_settings_list[i]["key"],
                    "value": existing_settings_list[i]["value"],
                }
                data["items"].append(item)

        return json.dumps(data)
