from playwright.sync_api import sync_playwright, expect

def test1():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/registration')
        email_input = page.get_by_test_id('registration-form-email-input').locator('input')
        email_input.fill('powder@gmail.com')
        username_input = page.get_by_test_id('registration-form-username-input').locator('input')
        username_input.focus()
        page.keyboard.type('powder')
        password_input = page.get_by_test_id('registration-form-password-input').locator('input')
        password_input.fill('powder')
        register_button = page.get_by_test_id('registration-page-registration-button')
        register_button.click()
        context.storage_state(path='new_session.json')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(storage_state="new_session.json")
        page = context.new_page()
        page.goto('https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/courses')
        courses_title = page.get_by_test_id('courses-drawer-list-item-title-text').locator('span')
        expect(courses_title).to_have_text('Courses')
        courses_title.click()
        empty_block = page.get_by_test_id('courses-list-empty-view-title-text')
        expect(empty_block).to_have_text('There is no results')
        empty_icon = page.get_by_test_id('courses-list-empty-view-icon')
        expect(empty_icon).to_be_visible()
        empty_block_description = page.get_by_test_id('courses-list-empty-view-description-text')
        expect(empty_block_description).to_have_text('Results from the load test pipeline will be displayed here')