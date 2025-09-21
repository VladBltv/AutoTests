from pages.base_page import BasePage
from playwright.sync_api import Page, expect

class CreateCoursePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title_create_course = page.get_by_test_id('create-course-toolbar-title-text')
        self.accept_create_course_button = page.get_by_test_id('create-course-toolbar-create-course-button')
        self.empty_icon_image_course = page.get_by_test_id('create-course-preview-empty-view-icon')
        self.no_image_title = page.get_by_test_id('create-course-preview-empty-view-title-text')
        self.no_image_description = page.get_by_test_id('Preview of selected image will be displayed here')
        self.upload_image_icon = page.get_by_test_id('create-course-preview-image-upload-widget-info-icon')
        self.title_upload_image = page.get_by_test_id('create-course-preview-image-upload-widget-info-title-text')
        self.recommendation_description_upload_image = page.get_by_test_id('create-course-preview-image-upload-widget-info-description-text')
        self.upload_image_input = page.get_by_test_id('create-course-preview-image-upload-widget-input')
        self.create_course_title_area = page.get_by_test_id('create-course-form-title-input').locator('input')
        self.create_course_estimate_area = page.get_by_test_id('create-course-form-estimated-time-input').locator('input')
        self.create_course_description_area = page.get_by_test_id('create-course-form-description-input').first
        self.create_course_max_score_area = page.get_by_test_id('create-course-form-max-score-input').locator('input')
        self.create_course_min_score_area = page.get_by_test_id('create-course-form-min-score-input').locator('input')
        self.exercises_title = page.get_by_test_id('create-course-exercises-box-toolbar-title-text')
        self.exercises_empty_icon = page.get_by_test_id('create-course-exercises-empty-view-icon')
        self.exercises_empty_title = page.get_by_test_id('create-course-exercises-empty-view-title-text')
        self.exercises_empty_description = page.get_by_test_id('create-course-exercises-empty-view-description-text')
        self.add_exercises = page.get_by_test_id('AddIcon')
        self.delete_exercises_button_list = page.get_by_test_id('DeleteOutlineOutlinedIcon')
        self.delete_course_image_button = page.get_by_test_id('create-course-preview-image-upload-widget-remove-button')

    def check_number_new_exercise(self, index: int):
        number_exercise = self.page.get_by_test_id(f'create-course-exercise-{index}-box-toolbar-subtitle-text')
        expect(number_exercise).to_be_visible()
        expect(number_exercise).to_have_text(f'#{index+1} Exercise')

    def check_title_new_exercise(self, index: int):
        title_exercise = self.page.get_by_test_id(f'create-course-exercise-form-title-{index}-input').locator('input')
        expect(title_exercise).to_be_visible()

    def fill_new_exercise_title(self, index: int, text: str):
        title_exercise = self.page.get_by_test_id(f'create-course-exercise-form-title-{index}-input').locator('input')
        expect(title_exercise).to_be_visible()
        title_exercise.fill(text)
        expect(title_exercise).to_have_text(text)

    def check_description_new_exercise(self, index):
        description_exercise = self.page.get_by_test_id(
            f'create-course-exercise-form-description-{index}-input').locator('input')
        expect(description_exercise).to_be_visible()

    def fill_new_exercise_description(self, index, text):
        description_exercise = self.page.get_by_test_id(
            f'create-course-exercise-form-description-{index}-input').locator('input')
        expect(description_exercise).to_be_visible()
        description_exercise.fill(text)
        expect(description_exercise).to_have_text(text)

    def delete_exercise(self, index):
        self.delete_exercises_button_list.nth(index).click()

    def check_title_create_course_page(self):
        expect(self.title_create_course).to_be_visible()

    def check_status_image_course(self, image_upload: bool = False):
        expect(self.upload_image_icon).to_be_visible()

        expect(self.title_upload_image).to_be_visible()
        expect(self.title_upload_image).to_have_text(
            'Tap on "Upload image" button to select file')

        expect(self.recommendation_description_upload_image).to_be_visible()
        expect(self.recommendation_description_upload_image).to_have_text(
            'Recommended file size 540X300'
        )
        expect(self.upload_image_input).to_be_visible()

        if image_upload:
            expect(self.delete_course_image_button).to_be_visible()
        else:
            expect(self.empty_icon_image_course).to_be_visible()

            expect(self.no_image_title).to_be_visible()
            expect(self.no_image_title).to_have_text('No image selected')

            expect(self.no_image_description).to_be_visible()
            expect(self.no_image_description).to_have_text(
                'Preview of selected image will be displayed here')

            expect(self.delete_course_image_button).not_to_be_visible()



    def load_image_to_course(self, image):
        self.upload_image_input.set_input_files(image)

    def edit_title_course(self, text):
        expect(self.title_create_course).to_be_visible()
        self.title_create_course.fill(text)
        expect(self.title_create_course).to_have_text(text)

    def edit_estimate_time(self, time):
        expect(self.create_course_estimate_area).to_be_visible()
        self.create_course_estimate_area.fill(time)
        expect(self.create_course_estimate_area).to_have_text(time)

    def edit_description(self, text):
        expect(self.create_course_description_area).to_be_visible()
        self.create_course_description_area.fill(text)
        expect(self.create_course_description_area).to_have_text(text)

    def edit_max_score(self, score):
        expect(self.create_course_max_score_area).to_be_visible()
        self.create_course_max_score_area.fill(score)
        expect(self.create_course_max_score_area).to_have_text(score)

    def edit_min_score(self, score):
        expect(self.create_course_min_score_area).to_be_visible()
        self.create_course_min_score_area.fill(score)
        expect(self.create_course_min_score_area).to_have_text(score)

    def add_exercise(self):
        expect(self.add_exercises).to_be_visible()
        self.add_exercises.click()

    def click_create_course_button(self):
        expect(self.accept_create_course_button).to_be_visible()
        self.accept_create_course_button.click()

    def check_disable_create_course_button(self):
        expect(self.accept_create_course_button).to_be_disabled()