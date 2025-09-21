from playwright.sync_api import Page, expect
from pages.base_page import BasePage
class CoursesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.course_main_title = page.get_by_test_id('courses-list-toolbar-title-text')
        self.create_course_button = page.get_by_test_id('courses-list-toolbar-create-course-button')
        self.empty_icon = page.get_by_test_id('courses-list-empty-view-icon')
        self.title_empty_course = page.get_by_test_id('courses-list-empty-view-title-text')
        self.description_empty_course = page.get_by_test_id('Results from the load test pipeline will be displayed here')
        self.course_title = page.get_by_test_id('course-widget-title-text')
        self.course_photo = page.get_by_test_id('course-preview-image')
        self.course_max_score = page.get_by_test_id('course-max-score-info-row-view-text')
        self.course_min_score = page.get_by_test_id('course-min-score-info-row-view-text')
        self.course_estimate = page.get_by_test_id('course-estimated-time-info-row-view-text')
        self.dropdown_course_button = page.get_by_test_id('MoreVertIcon')
        self.edit_course = page.get_by_test_id('course-view-edit-menu-item')
        self.delete_course = page.get_by_test_id('course-view-delete-menu-item')

    def check_course_title(self):
        expect(self.course_main_title).to_be_visible()
        expect(self.course_main_title).to_have_text('Courses')

    def check_create_course_button(self):
        expect(self.create_course_button).to_be_visible()

    def click_create_course_button(self):
        self.create_course_button.click()

    def check_course_info(self, index: int, title: str, max_score: str, min_score: str, estimate: str):
        expect(self.course_title.nth(index)).to_be_visible()
        expect(self.course_title.nth(index)).to_have_text(title)

        expect(self.course_photo.nth(index)).to_be_visible()

        expect(self.course_max_score.nth(index)).to_be_visible()
        expect(self.course_max_score.nth(index)).to_have_text(max_score)

        expect(self.course_min_score.nth(index)).to_be_visible()
        expect(self.course_min_score.nth(index)).to_have_text(min_score)

        expect(self.course_estimate.nth(index)).to_be_visible()
        expect(self.course_estimate.nth(index)).to_have_text(estimate)

    def click_dropdown_course(self, index):
        self.dropdown_course_button.nth(index).click()
        expect(self.edit_course).to_be_visible()
        expect(self.delete_course).to_be_visible()

    def click_edit_course(self, index):
        self.edit_course.nth(index).click()

    def click_delete_course(self, index):
        self.delete_course.nth(index).click()

    def check_empty_courses(self):
        expect(self.empty_icon).to_be_visible()

        expect(self.title_empty_course).to_be_visible()
        expect(self.title_empty_course).to_have_text('There is no results')

        expect(self.description_empty_course).to_be_visible()
        expect(self.description_empty_course).to_have_text('Results from the load test pipeline will be displayed here')

