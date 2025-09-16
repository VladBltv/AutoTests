import json


class Payloads:
    def get_users_list(self, query, page, per_page):
        return json.dumps({"query": query, "page": page, "perPage": per_page})

    def user_login(self, login, password):
        return json.dumps({"login": login, "password": password})
