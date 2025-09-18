from playwright.sync_api import sync_playwright

class RegistrationPage:
    def __init__(self, page):
        self.page = page
        self.email_input = self.page.get_by_test_id('registration-form-email-input').locator('input')
        self.username_input = self.page.get_by_test_id('registration-form-username-input').locator('input')
        self.password_input = self.page.get_by_test_id('registration-form-password-input').locator('input')
        self.button_register = self.page.get_by_test_id('registration-page-registration-button')

    def fill_email_input(self, email):
        self.email_input.fill(email)

    def fill_username_input(self, username):
        self.username_input.fill(username)

    def fill_password_input(self, password):
        self.password_input.fill(password)

    def click_register_button(self):
        self.button_register.click()