from befree.api_model.cocreate.public.main_page.api_main_page import MainPage
from befree.api_model.cocreate.public.users.api_users import Users
from befree.api_model.cocreate.public.contests.api_contests import Contests
from befree.api_model.cocreate.public.works.api_works import Works


class CocreatePublic:
    api_main_page = MainPage()
    api_users_pub = Users()
    api_contests_pub = Contests()
    api_works_pub = Works()
