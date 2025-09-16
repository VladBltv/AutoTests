from befree.api_model.cocreate.private.users.api_users import Users
from befree.api_model.cocreate.private.collaborations.api_collaborations import Collaborations
from befree.api_model.cocreate.private.catalog.api_catalog import Catalog
from befree.api_model.cocreate.private.contests.api_contests import Contests
from befree.api_model.cocreate.private.menu.api_menu import Menu
from befree.api_model.cocreate.private.settings.api_settings import Settings
from befree.api_model.cocreate.private.options.api_options import Options
from befree.api_model.cocreate.private.works.api_works import Works


class CocreatePrivate:
    api_users = Users()
    api_collaborations = Collaborations()
    api_catalog = Catalog()
    api_contests = Contests()
    api_menu = Menu()
    api_settings = Settings()
    api_options = Options()
    api_works = Works()
