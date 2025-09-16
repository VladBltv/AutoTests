class Endpoints:
    get_users_list = "/users"
    user_login = "/users/login"
    get_user = lambda self, user_id: f"/users/{user_id}/show"
