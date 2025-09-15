class Locators:
    def __init__(self, page):
        self.email_input = page.get_by_test_id('registration-form-email-input').locator('input')
        self.username_input = page.get_by_test_id('registration-form-username-input').locator('input')
        self.password_input = page.get_by_test_id('registration-form-password-input').locator('input')
        self.register_button = page.get_by_test_id('registration-page-registration-button')
        self.auth_title = page.get_by_test_id('dashboard-drawer-list-item-title-text').locator('span')