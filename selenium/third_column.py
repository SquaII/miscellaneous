#-*- coding:utf8 -*-
from selenium.common.exceptions import NoSuchElementException


def get_current_chain_subject(web_obj):
    subject = "".join(("//div[@id='mo.mcl-col-2']",
        "//div[@class='chain members']//div[@class='subject']"))
    chain_subject = web_obj.find_element(subject)
    return chain_subject.text


def letters_amount(web_obj):
    counter = 1
    while True:
        letter = "".join(("//div[@id='mo.mcl-col-2']",
            "//div[@class='chain members']/div[4]/div[{0}]".format(counter)))
        try:
            web_obj.driver.find_element_by_xpath(letter)
        except NoSuchElementException:
            break
        counter += 1
    print "Selected chain '{0}' contain {1} letters.".format(
        get_current_chain_subject(web_obj), counter - 1)
    return counter - 1


def open_letters(web_obj, number_list=None):
    counter = letters_amount(web_obj)
    if number_list is None:
        generator = xrange(1, counter + 1)
    else:
        for number in number_list:
            if not 0 < number < counter:
                number_list.remove(str(number))
    for letter_number in generator:
        letter = "".join(("//div[@id='mo.mcl-col-2']",
            "//div[@class='chain members']/div[4]",
            "/div[{0}]".format(letter_number),
            "//div[@class='body_wrapper']"))
        try:
            letter_obj = web_obj.driver.find_element_by_xpath(letter)
        except NoSuchElementException:
            letter_obj = web_obj.find_element(letter.replace('body', 'title'),
                click=True)
            letter_obj.click()
