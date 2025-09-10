from playwright.sync_api import expect
import pytest

def test1():
    print('test1')

def test2():
    print('test1')

def test3():
    print('test1')

def test4():
    print('test1')

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