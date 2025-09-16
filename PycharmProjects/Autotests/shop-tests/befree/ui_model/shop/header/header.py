from playwright.sync_api import Page
from befree.ui_model.shop.header.locators import Locators
from befree.ui_model.shop.states import States


class Header:
    def __init__(self, page: Page):
        self._locators = Locators(page)
        self._states = States()

    # samples
    def click_burger(self):
        self._locators.burger.click()

    def hover_burger(self):
        self._locators.burger.hover()

    def click_logo(self):
        self._locators.logo.click()

    def click_city_link(self):
        self._locators.city_link.click()

    def click_profile_button(self):
        self._locators.profile_button.click()

    def click_favorites_button(self):
        self._locators.favorites_button.click()

    def click_cart_button(self):
        self._locators.cart_button.click()

    def change_city(self, city_name="Санкт-Петербург"):
        self._locators.city_link.click()

        try:
            if self._locators.city(city_name=city_name).is_visible():
                self._locators.city(city_name=city_name).click()
            else:
                print(f"Элемент с городом {city_name} не виден на странице")
        except Exception:
            print(f"Элемент с городом {city_name} не найден")

        actual_city = self._locators.city_link.inner_text()
        if actual_city != city_name:
            print(f"Город не изменился: ожидалось '{city_name}', получено '{actual_city}'")






