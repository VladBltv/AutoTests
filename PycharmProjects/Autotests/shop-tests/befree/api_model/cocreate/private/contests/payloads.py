import json
from datetime import datetime, timedelta
from mimesis import Text, Internet
from befree.api_model.cocreate import utils
from befree.api_model.cocreate.private.users.api_users import Users

# from befree.api_model.cocreate.private.contests.api_contests import Contests


class Payloads:
    def get_contests(self, query, visibility, page, per_page, **kwargs):
        payload = json.dumps(
            {
                "query": query,
                "filter": {"visibility": visibility},
                "page": page,
                "perPage": per_page,
            }
        )

        return payload

    def create_contest(self, **kwargs):
        data = {}

        if "title" in kwargs:
            if kwargs["title"] is not None:
                data["title"] = kwargs.pop("title")
        else:
            data["title"] = Text("ru").title()[:200] + str(int(datetime.now().timestamp()))

        if "slug" in kwargs:
            if kwargs["slug"] is not None:
                data["slug"] = kwargs.pop("slug")
        else:
            data["slug"] = Internet().slug(parts_count=3)

        if "announcement" in kwargs:
            if kwargs["announcement"] is not None:
                data["announcement"] = kwargs.pop("announcement")
        else:
            data["announcement"] = Text("ru").sentence()[:150]

        if "concept" in kwargs:
            if kwargs["concept"] is not None:
                data["concept"] = kwargs.pop("concept")
        else:
            data["concept"] = Text("ru").sentence()[:400]

        if "conditions" in kwargs:
            if kwargs["conditions"] is not None:
                data["conditions"] = kwargs.pop("conditions")
        else:
            data["conditions"] = Text("ru").sentence()[:300]

        if "skills" in kwargs:
            if kwargs["skills"] is not None:
                data["skills"] = kwargs.pop("skills")
        else:
            data["skills"] = Text("ru").sentence()[:300]

        if "prize" in kwargs:
            if kwargs["prize"] is not None:
                data["prize"] = kwargs.pop("prize")
        else:
            data["prize"] = Text("ru").sentence()[:150]

        if "audiencePrize" in kwargs:
            if kwargs["audiencePrize"] is not None:
                data["audiencePrize"] = kwargs.pop("audiencePrize")
        else:
            data["audiencePrize"] = Text("ru").sentence()[:150]

        if "visible" in kwargs:
            if kwargs["visible"] is not None:
                data["visible"] = kwargs.pop("visible")
        else:
            data["visible"] = "1"

        if "isVisibleOnMainPage" in kwargs:
            if kwargs["isVisibleOnMainPage"] is not None:
                data["isVisibleOnMainPage"] = kwargs.pop("isVisibleOnMainPage")
        else:
            data["isVisibleOnMainPage"] = "0"

        params = dict()
        if "winnersCount" in kwargs:
            if kwargs["winnersCount"] is not None:
                params["params[winnersCount]"] = kwargs.pop("winnersCount")
        else:
            params["params[winnersCount]"] = 1

        if "audienceWinnersCount" in kwargs:
            if kwargs["audienceWinnersCount"] is not None:
                params["params[audienceWinnersCount]"] = kwargs.pop("audienceWinnersCount")
        else:
            params["params[audienceWinnersCount]"] = 1

        referees = dict()
        if "referees" in kwargs:
            if kwargs["referees"] is not None:
                referees_qty = len(kwargs["referees"])
                referees_ids = kwargs.pop("referees")
                referees_keys = [f"referees[{i}]" for i in range(0, referees_qty)]
                referees = dict(map(lambda *args: args, referees_keys, referees_ids))
        else:
            users_response = Users().get_list()
            referees = dict({"referees[0]": users_response.json()["data"]["users"][0]["id"]})

        dates = dict()
        if "dates" in kwargs:
            if kwargs["dates"] is not None:
                dates_parts = kwargs.pop("dates")
                dates["dates[start]"] = dates_parts["start"]
                dates["dates[endOfAcceptanceOfWork]"] = dates_parts["endOfAcceptanceOfWork"]
                dates["dates[finish]"] = dates_parts["finish"]
        else:
            dates["dates[start]"] = (datetime.today() + timedelta(1)).strftime("%Y-%m-%dT00:00")
            dates["dates[endOfAcceptanceOfWork]"] = (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00")
            dates["dates[finish]"] = (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00")

        data = {**data, **dates, **referees, **params}

        return data

    def update_contest(self, **kwargs):
        """kwargs should contain current_data"""
        data = {}

        current_data = kwargs.pop("current_data") if "current_data" in kwargs else {}

        if len(current_data.keys()) > 0:
            old_referees_count = len(current_data["referees"])

            for key in current_data:
                if key in ["dates"]:
                    for i in current_data[key]:
                        data[f"{key}[{i}]"] = current_data[key][i]
                    continue
                if key == "referees":
                    for j in range(0, len(current_data[key])):
                        data[f"{key}[{j}]"] = current_data[key][j]["id"]
                    continue
                if key in ["visible", "isVisibleOnMainPage"]:
                    data[key] = 1 if current_data[key] is True else 0
                    continue
                if key in ["images", "id", "status", "rules"]:
                    continue
                if key == "params":
                    for k in current_data[key]:
                        data[f"{key}[{k}]"] = current_data[key][k]
                    continue
                data[key] = current_data[key]
        else:
            data = dict(
                {
                    "title": Text("ru").title()[:200] + str(int(datetime.now().timestamp())),
                    "slug": Internet().slug(parts_count=3),
                    "announcement": Text("ru").sentence()[:100],
                    "concept": Text("ru").sentence()[:100],
                    "conditions": Text("ru").sentence()[:100],
                    "skills": Text("ru").sentence()[:100],
                    "prize": Text("ru").sentence()[:100],
                    "audiencePrize": Text("ru").sentence()[:100],
                    "referees[0]": 1,
                    "visible": 1,
                    "isVisibleOnMainPage": 0,
                    "dates[start]": (datetime.today() + timedelta(1)).strftime("%Y-%m-%dT00:00"),
                    "dates[endOfAcceptanceOfWork]": (datetime.today() + timedelta(10)).strftime("%Y-%m-%dT00:00"),
                    "dates[finish]": (datetime.today() + timedelta(20)).strftime("%Y-%m-%dT00:00"),
                    "params[winnersCount]": 1,
                    "params[audienceWinnersCount]": 1,
                }
            )

        if kwargs:
            for key in kwargs:
                if kwargs[key] is None:
                    if key in ["images", "rules"]:
                        continue
                    if key == "dates":
                        data.pop("dates[start]")
                        data.pop("dates[endOfAcceptanceOfWork]")
                        data.pop("dates[finish]")
                        continue
                    if key == "referees":
                        i = 0
                        for i in range(0, old_referees_count):
                            data.pop(f"referees[{i}]")
                        continue
                    if key == "winnersCount":
                        data.pop("params[winnersCount]")
                    if key == "audienceWinnersCount":
                        data.pop("params[audienceWinnersCount]")
                    data.pop(key)
                    continue
                if kwargs[key] is not None:
                    if key == "dates":
                        data["dates[start]"] = kwargs[key]["start"]
                        data["dates[endOfAcceptanceOfWork]"] = kwargs[key]["endOfAcceptanceOfWork"]
                        data["dates[finish]"] = kwargs[key]["finish"]
                        continue
                    if key == "referees":
                        i = 0
                        for i in range(0, old_referees_count):
                            data.pop(f"referees[{i}]")
                        j = 0
                        for j in range(0, len(kwargs[key])):
                            data[f"{key}[{j}]"] = kwargs[key][j]
                        continue
                    if key == "winnersCount":
                        data["params[winnersCount]"] = kwargs["winnersCount"]
                        continue
                    if key == "audienceWinnersCount":
                        data["params[audienceWinnersCount]"] = kwargs["audienceWinnersCount"]
                        continue
                    data[key] = kwargs[key]

        return data

    def files(self, **kwargs):
        images = {}
        rules = {}

        if "images" in kwargs:
            if kwargs["images"] is not None:
                images = kwargs.pop("images")
        else:
            images = utils.set_contest_images()

        if "rules" in kwargs:
            if kwargs["rules"] is not None:
                rules = kwargs.pop("rules")
        else:
            rules = utils.set_contest_rules()

        files = {**images, **rules}

        return files
