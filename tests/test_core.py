from playwright.sync_api import expect
import pytest

@pytest.mark.parametrize('users', ['Vlad', 'Alena', 'Masha', 'Anton'], ids=('man', 'woman', 'woman', 'man'))
class TestLesson:
    def test1(self, users):
        print(users)

    @pytest.fixture(params=[1, 2, 3])
    def sss(self, request, users):
        print(request.param)

    def test3(self, users):
        print(users)

    @pytest.mark.usefixtures('testfixture')
    def test4(self, users):
        print('test_4')

@pytest.mark.parametrize('email, password', [('user.name@gmail.com', 'password'), ('user.name@gmail.com', '  '), ('  ', 'password')])
def test_wrong_email_or_password_authorization(email, password):
    print(email, password)
@pytest.mark.usefixtures('initialize_browser_state')
def test_empty_courses_list(chromium_page_with_state):
    chromium_page_with_state.goto('https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/courses')
    courses_title = chromium_page_with_state.get_by_test_id('courses-list-toolbar-title-text')
    expect(courses_title).to_have_text('Courses')
    empty_icon = chromium_page_with_state.get_by_test_id('courses-list-empty-view-icon')
    expect(empty_icon).to_be_visible()
    no_result_text = chromium_page_with_state.get_by_test_id('courses-list-empty-view-title-text')
    expect(no_result_text).to_have_text('There is no results')
    reason_text = chromium_page_with_state.get_by_test_id('courses-list-empty-view-description-text')
    expect(reason_text).to_have_text('Results from the load test pipeline will be displayed here')