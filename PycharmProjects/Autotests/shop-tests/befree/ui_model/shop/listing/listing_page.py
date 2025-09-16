from playwright.sync_api import Page, expect
from befree.ui_model.shop.listing.locators import Locators
from befree.ui_model.shop.states import States


class ListingPage:
    def __init__(self, page: Page):
        self._locators = Locators(page)
        self._states = States()

    def navigate(self, slug, gender="zhenskaya"):
        """Переход на страницу листинга"""
        self._locators.page.goto(url=f"{gender}/{slug}")

    def check_subcategories_exist(self):
        """Проверяем, что на странице присутствует блок с субкатегориями"""
        expect(self._locators.subcategories).to_be_visible()

    def check_flocktory_container_exist(self):
        """Проверяем, что на странице присутствует класс для виджета флоктори для вывода субкатегорий"""
        expect(self._locators.flocktory_container).to_be_visible()
