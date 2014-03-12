#-*- coding:utf8 -*-
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException


class WebBrowser(object):

    def __init__(self, driver, mail_url, gui, testing_on_komtet, login,
                 password, system_tags):
        self.driver = driver
        self.mail_url = mail_url
        self.gui = gui
        self.testing_on_komtet = testing_on_komtet
        self.login = login
        self.password = password
        self.system_tags = system_tags
        self.create_window()

    def create_window(self):
        print "LOGINING..."
        self.driver.get(self.mail_url)
        if self.gui:
            self.driver.maximize_window()
        else:
            self.driver.set_window_size(1700, 1000)
        self.sign_in()

    def sign_in(self):
        login = "//*[@id='sin_login']"
        try:
            self.driver.find_element_by_xpath(login)
        except NoSuchElementException:
            login = "//*[@id='username']"
            self.driver.find_element_by_xpath(login)
            self.testing_on_komtet = True
        self.find_element(login, typing=self.login)

        if self.testing_on_komtet:
            password = "//*[@id='password']"
        else:
            password = "//*[@id='sin_password']"
        self.find_element(password, typing=self.password)

        sign_in_button = "//button[@type='submit']"
        self.find_element(sign_in_button, click=True)
        print "ENTERING THE MAIL"
        self.wait_for_refresh_second_column()

    def wait_for_update(self):
        flag = False
        update_bubble = "//div[@class='hint_message']"
        counter = 400
        while True:
            counter -= 1
            if not counter:
                break
            try:
                self.driver.find_element_by_xpath(update_bubble)
                flag = True
            except (NoSuchElementException, StaleElementReferenceException):
                if flag:
                    break

    def wait_for_sending(self):
        send_button = "//div[@id='mo.mcl-col-2']//a[@title='Send']"
        while True:
            try:
                self.driver.find_element_by_xpath(send_button)
            except (StaleElementReferenceException, NoSuchElementException,
                    AttributeError):
                break

    def wait_for_refresh_second_column(self):
        self.wait_for_refresh(1)

    def wait_for_refresh_third_column(self):
        self.wait_for_refresh(2)

    def wait_for_refresh(self, number):
        waiting = "//div[@id='mo.mcl-col-{0}']".format(number)
        while True:
            waiting_attr = self.find_element(waiting, attribute="class")
            if waiting_attr == "panel":
                break

    def find_element(self, target_link, click=False, attribute="", typing="",
                     hover=False):
        counter = 1000
        while counter:
            counter -= 1
            if not counter:
                raise Exception
            try:
                target = self.driver.find_element_by_xpath(target_link)
                if attribute:
                    return target.get_attribute(attribute)
                if click and target.is_displayed():
                    target.click()
                    return True
                if typing:
                    return target.send_keys(typing)
                if hover:
                    ActionChains(self.driver).move_to_element(target).perform()
                    break
                return target
            except (StaleElementReferenceException, NoSuchElementException):
                pass

    def element_exists(self, target_link):
        counter = 100
        while counter:
            # print "EXISTS ", target_link
            counter -= 1
            try:
                self.driver.find_element_by_xpath(target_link)
                return True
            except (NoSuchElementException, StaleElementReferenceException):
                pass
        return False

    def switch_to_message_body(self):
        self.driver.switch_to_default_content()
        body_frame = "".join(("//div[@id='mo.mcl-col-2']",
            "//td[@class='mceIframeContainer mceFirst mceLast']/iframe"))
        body_frame_obj = self.find_element(body_frame)
        self.driver.switch_to_frame(body_frame_obj)
