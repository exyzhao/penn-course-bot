from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import secrets

import time
from selenium.webdriver.common.action_chains import ActionChains


def find_register_function(html_content):
    """
    Uses BeautifulSoup to find the 'register' JavaScript function on the main page
    :param html_content: raw html page input
    :return: function to navigate to register page
    """
    soup = BeautifulSoup(html_content, features="html.parser")
    element = soup.body.ul.li.ul.contents[7].a
    return element['onclick'][7:]


def check_enrolled(html_content, subject, course, section):
    """
    Uses BeautifulSoup to check if the user is already enrolled in the course
    :param html_content: raw html page input
    :param subject: 3-4 letter department code (eg. "CIS")
    :param course: Course Number (eg. "120")
    :param section: Section Number (eg. "001")
    :return True if enrolled already, false otherwise

    """
    soup = BeautifulSoup(html_content, features="html.parser")
    if len(subject) == 3:
        course_string = f"{subject} -{course}-{section}"
    else:
        course_string = f"{subject}-{course}-{section}"
    if soup.findAll(text=course_string):
        print(f"Already Enrolled in {course_string}")
        return True
    else:
        print(f"Not Already Enrolled in {course_string}")
        return False


def init_driver():
    """
    Initializes chrome driver. You need to set your own chrome driver path.
    https://sites.google.com/a/chromium.org/chromedriver/downloads
    :return: driver instance
    """
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    chrome_options.add_argument('no-sandbox')
    driver = webdriver.Chrome(
        executable_path="../../Downloads/chromedriver",
        options=chrome_options)
    return driver


def intouch_signup(driver, subject, course, section):
    """
    Main method to register for courses
    :param driver: driver instance
    :param subject: 3-4 letter department code (eg. "CIS")
    :param course: Course Number (eg. "120")
    :param section: Section Number (eg. "001")
    :return: 0 if successful, 1 otherwise
    """
    # driver.get("https://pennintouch.apps.upenn.edu/")
    driver.get("https://courses.upenn.edu/")

    actions = ActionChains(driver)

    elem = driver.find_element_by_id("primary-cart-button")
    elem.click()

    # Check if login prompt appears
    handles = driver.window_handles
    if len(handles) != 1:

        # Switch to login popup window
        main_window = driver.current_window_handle
        for handle in handles:
            if handle != main_window:
                driver.switch_to_window(handle)

        # Logs the user in
        if "Log In" in driver.title:
            elem = driver.find_element_by_name("j_username")
            elem.clear()
            elem.send_keys(secrets.PENNKEY)

            elem = driver.find_element_by_name("j_password")
            elem.clear()
            elem.send_keys(secrets.PENNKEY_PASS)
            elem.send_keys(Keys.RETURN)

            driver.switch_to_window(main_window)
            elem = driver.find_element_by_class_name("sam-wait__button--login")
            elem.click()
            time.sleep(5)
            elem = driver.find_element_by_class_name("sam-wait__button--login")
            elem.click()
            time.sleep(5)
            elem = driver.find_element_by_class_name("sam-wait__button--login")
            elem.click()
            time.sleep(5)
            elem = driver.find_element_by_class_name("sam-wait__button--login")
            elem.click()
            time.sleep(5)
            elem = driver.find_element_by_class_name("sam-wait__button--login")
            elem.click()
            time.sleep(5)
            # driver.refresh()
            # elem = driver.find_element_by_id("primary-cart-button")
            # elem.click()

            # handles = driver.window_handles
            # for handle in handles:
            #     print(handle)
            #     if handle != main_window:
            #         driver.switch_to_window(handle)
            # time.sleep(0.5)
            # driver.switch_to_window(main_window)
            time.sleep(5)

    # # Navigate to the registration page
    # js_function = find_register_function(driver.page_source)
    # driver.execute_script(js_function)

    # try:
    #     driver.implicitly_wait(1)  # wait for classes to populate
    #     if check_enrolled(driver.page_source, subject, course, section):
    #         driver.close()
    #         return 0
    #     subject_select = Select(driver.find_element_by_name("subjectPrimary"))
    #     subject_select.select_by_value(subject)
    #     course_select = Select(driver.find_element_by_name("courseNumberPrimary"))
    #     course_select.select_by_value(course)
    #     section_select = Select(driver.find_element_by_name("sectionNumberPrimary"))
    #     section_select.select_by_value(section)
    #     request_button = driver.find_element_by_class_name("fastGreenButton")
    #     request_button.click()
    #     print(f"Success! - {subject} {course} {section} was registered")
    # except NoSuchElementException or NameError:
    #     print(f"Failed - {subject} {course} {section} is not available")
    #     # driver.close()
    #     return 1
    # # driver.close()
    # return 0


if __name__ == '__main__':
    chrome_driver = init_driver()
    # intouch_signup(chrome_driver, "MGMT", "230", "003")
