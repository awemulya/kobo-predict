from django.test import TestCase

# Create your tests here.

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class AccountTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(AccountTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(AccountTestCase, self).tearDown()

    def click_n_wait(driver, timeout=5):
        source = driver.page_source
        def compare_source(driver):
            try:
                return source != driver.page_source
            except WebDriverException:
                pass
        WebDriverWait(driver, timeout).until(compare_source)

    def test_register(self):
        selenium = self.selenium
        #Opening the link we want to test
        selenium.get('http://127.0.0.1:8001/fieldsight/organization/')
        #find the form element
        print "Sucess"
        # first_name = selenium.find_element_by_id('id_first_name')
        # last_name = selenium.find_element_by_id('id_last_name')
        # username = selenium.find_element_by_id('id_username')
        # email = selenium.find_element_by_id('id_email')
        # password1 = selenium.find_element_by_id('id_password1')
        # password2 = selenium.find_element_by_id('id_password2')

        # submit = selenium.find_element_by_name('register')

        # #Fill the form with data
        # first_name.send_keys('Yusuf')
        # last_name.send_keys('Unary')
        # username.send_keys('unary')
        # email.send_keys('yusuf@qawba.com')
        # password1.send_keys('123456')
        # password2.send_keys('123456')

        # #submitting the form
        # submit.send_keys(Keys.RETURN)

        #check the returned result
assert 'Check your email' in selenium.page_source

