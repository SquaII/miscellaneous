#-*- coding:utf8 -*-
import sys
import os
import tkMessageBox

from selenium import webdriver
from pyvirtualdisplay import Display
from helpers import read_config
from test_cases import *
from browser import WebBrowser
from letters import DraftManager, SendingManager


if __name__ == "__main__":
    # reading from config
    config_dict = read_config()
    GUI = int(config_dict["GUI"][0])
    BROWSER = config_dict["BROWSER"][0].lower()
    CHROMEDRIVER_PATH = config_dict["CHROMEDRIVER_PATH"][0]
    MAIL_URL = config_dict["MAIL_URL"][0]
    LOGIN = config_dict["LOGIN"][0]
    PASSWORD = config_dict["PASSWORD"][0]
    ATTACHMENTS = config_dict["ATTACHMENTS"]
    DESTINATION = config_dict["DESTINATION"][0]
    INLINES = config_dict["INLINES"]
    CC = config_dict["CC"]
    BCC = config_dict["BCC"]
    REPLY_TO = config_dict["REPLY_TO"]
    SYSTEM_TAGS = ["inbox", "starred", "sent", "drafts", "trash", "all",
        "spam"]
    TEST_TAGS = ["tag_test 1", "tag_test 2", "tag_test 3", "tag_test4"]
    TESTING_ON_KOMTET = False
    TEST_REPORT = ""

    MODE = sys.argv[1] if len(sys.argv) > 1 else ""

    if MODE == "-h" or MODE == "--help":
        print "\n".join((
              "    -h or help   for help",
              "    -l          sending single letter",
              "    -d          creating single draft",
              "    -m          sending many letters",
              "    -u          creating many drafts",
              "    -t          simple tags testing",
              "    -c          complex tags testing",
              "    -f          sending fast chain"))
        sys.exit()

    if not GUI:
        display = Display(visible=0, size=(800, 600))
        display.start()
    # creating web-objects
    if BROWSER == "chrome":
        if not CHROMEDRIVER_PATH:
            CHROMEDRIVER_PATH = os.path.realpath("chromedriver")
            DRIVER = webdriver.Chrome(CHROMEDRIVER_PATH)
    elif BROWSER == "firefox":
        DRIVER = webdriver.Firefox()

    test_obj = WebBrowser(DRIVER, MAIL_URL, GUI, TESTING_ON_KOMTET, LOGIN,
        PASSWORD, SYSTEM_TAGS)

    send_obj_t = SendingManager(test_obj.driver,
                                inlines=INLINES,
                                attachments=ATTACHMENTS,
                                cc=CC,
                                bcc=BCC,
                                reply_to=REPLY_TO
                                )

    send_obj_f = SendingManager(test_obj.driver,
                                attach_flag=False,
                                text_flag=False,
                                contacts_flag=False,
                                inline_flag=False,
                                reply_to_flag=False,
                                inlines=INLINES,
                                attachments=ATTACHMENTS,
                                cc=CC,
                                bcc=BCC,
                                reply_to=REPLY_TO
                                )

    draft_obj = DraftManager(test_obj.driver,
                             inlines=INLINES,
                             attachments=ATTACHMENTS,
                             cc=CC,
                             bcc=BCC,
                             reply_to=REPLY_TO
                             )

    TEST_REPORT = "\nВыполнено в {0}:\n\n".format(BROWSER)
    # action
    clear_context(test_obj, ["sent"])
    TEST_REPORT += "".join(("* Удаление цепочек с отправленными письмами\n"
        "* Очистка корзины\n"))

    if MODE == "-a" or "l" in MODE:
        single_letter_test(send_obj_t)
        TEST_REPORT += "* Отправка одиночного письма\n"
    if MODE == "-a" or "f" in MODE:
        fast_chain_test(send_obj_f)
        TEST_REPORT += "* Отправка быстрой цепочки писем\n"
    if MODE == "-a" or "m" in MODE:
        multiple_sending_test(send_obj_t)
        TEST_REPORT += "* Отправка цепочки писем\n"
    if MODE == "-a" or "t" in MODE:
        simple_tag_test(test_obj)
        TEST_REPORT += "* Проверка базового функционала тегов\n"
    if MODE == "-a" or "c" in MODE:
        complex_tag_test(send_obj_f)
        TEST_REPORT += "* Проверка фукционирования тегов в цепочках\n"
    if MODE == "-a" or "d" in MODE:
        single_draft_test(draft_obj)
        TEST_REPORT += "* Создание одного черновика\n"
    if MODE == "-a" or "u" in MODE:
        multiple_draft_test(draft_obj)
        TEST_REPORT += "* Создание цепочки черновиков\n"

    print TEST_REPORT
    tkMessageBox.showinfo("Тестирование завершено.", TEST_REPORT)

    # посчитать время раскрытия цепочки
