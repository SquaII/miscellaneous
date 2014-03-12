#-*- coding:utf8 -*-
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from tags import *


__all__ = ["chains_checkbox", "trash_button", "empty_trash_button",
    "refresh_button", "chains_combobox", "operate_chain_by_subject"]


def chains_in_column(web_obj):
    chains_existance = "".join(("//div[@id='mo.mcl-col-1']",
        "//div[@class='content']/div/a"))
    return web_obj.element_exists(chains_existance)


def chains_checkbox(web_obj, option):
    if not chains_in_column(web_obj):
        return
    combo_dict = {"all": 1, "none": 2, "read": 3, "unread": 4,
                  "has_attachment": 5, "has_no_attachment": 6, "inverse": 7}
    if option not in combo_dict.keys():
        print "No such option."
        return
    checkbox = "//div[@id='mo.mcl-col-1']//div[@name='combocheckbox']/a[1]"
    web_obj.find_element(checkbox, click=True)

    select = "".join(("//div[@id='mo.mcl-col-1']//div[@name='combocheckbox']",
        "/a[2]/span[{0}]".format(combo_dict.get(option))))
    web_obj.find_element(select, click=True)
    print "{0} chains selected.".format(option.capitalize())


def trash_button(web_obj):
    print "Deleting chains..."
    if not chains_in_column(web_obj):
        return
    trash = "//div[@id='mo.mcl-col-1']//i[@title='Delete selected chains']"
    web_obj.find_element(trash, click=True)
    web_obj.wait_for_refresh_second_column()
    print "Selected letters was deleted."


def empty_trash_button(web_obj):
    print "Deleting chains from trash..."
    if not chains_in_column(web_obj):
        return
    if current_tag(web_obj) == "trash":
        empty_trash = "//div[@id='mo.mcl-col-1']//i[@name='tag_empty']"
        web_obj.find_element(empty_trash, click=True)
        web_obj.driver.switch_to_alert().accept()
        web_obj.wait_for_refresh_second_column()
        print "All letters from 'Trash' devastated."
    else:
        print "Empty trash available only in 'Trash' context."


def refresh_button(web_obj):
    print "Creating second column..."
    refresh = "//div[@id='mo.mcl-col-1']//i[@title='Refresh chains']"
    web_obj.find_element(refresh, click=True)
    web_obj.wait_for_refresh_second_column()
    print "Second column refreshed."


def chains_combobox(web_obj, option):
    print "Selecting chains..."
    if not chains_in_column(web_obj):
        return
    combo_dict = {"Mark as read": 1, "Mark as unread": 2,
                  "Mark as spam": 3, "Mark as no spam": 4}
    if option not in combo_dict.keys():
        print "No such option."
        return
    combobox = "".join(("//div[@id='mo.mcl-col-1']",
        "//div[@class='momail ui combobox button text s26x26 drop-left']/a"))
    web_obj.find_element(combobox, True)

    select = "//div[@id='mo.mcl-col-1']//span[@title='{0}']".format(option)
    web_obj.find_element(select, click=True)
    print "Selected chains {0}.".format(option.lower())


def visible_chains_count(web_obj):
    if not chains_in_column(web_obj):
        return 0
    count = "//div[@id='mo.mcl-col-1']//div[@class='momail ui label']"
    count_attr = web_obj.find_element(count, attribute="data-range")
    return int(count_attr.partition('-')[2])


# =============Second column chain operations==================================
def operate_chain_by_subject(web_obj, chain_subject, command, tag_name=None):
    msg = ""
    pattern1 = "".join(("//div[@id='mo.mcl-col-1']",
        "//div[@class='content']/div/a[{0}]"))
    pattern2 = "//a[@href='{0}']//div[@class='row subject']"
    available_chains = visible_chains_count(web_obj)
    domain = ".ru" if TESTING_ON_KOMTET else ".com"

    for i in xrange(available_chains):
        chain_href_pattern = pattern1.format(i + 1)
        chain_attr = web_obj.find_element(chain_href_pattern, attribute="href")
        chain_href = chain_attr.partition(domain)[2]
        if not chain_href:
            chain_href = chain_attr.partition(":5003")[2]
        chain_title_pattern = pattern2.format(chain_href)
        chain_title = web_obj.find_element(chain_title_pattern,
            attribute="title")

        if chain_title in chain_subject:
            if command == "switch_check":
                switch_chain_check(web_obj, chain_href)
                msg = "checked"
            if command == "open_chain":
                open_chain(web_obj, chain_href, chain_title)
                msg = "opened"
            if command == "hang_tag":
                hang_tag(web_obj, chain_href, tag_name)
                msg = "tagged by tag '{0}'".format(tag_name)
            if command == "unhang_tag":
                msg = unhang_tag(web_obj, chain_href, tag_name)
            if command == "switch_star":
                switch_star(web_obj, chain_href)
                msg = "starred"
            if command == "count_letters":
                return chain_counter(web_obj, chain_href)
            if command == "check_tag":
                return check_tag(web_obj, chain_href, tag_name)
    print "Chains '{0}' {1}.".format(chain_subject, msg)


def switch_chain_check(web_obj, href):
    check = "".join(("//div[@id='mo.mcl-col-1']//a[@href='{0}']".format(href),
        "//input[@class='checkbox']"))
    web_obj.find_element(check, click=True)


def open_chain(web_obj, href, title):
    print "Opening chain..."
    global TEST_REPORT
    chain = "//div[@id='mo.mcl-col-1']//a[@href='{0}']".format(href)
    web_obj.find_element(chain, click=True)
    web_obj.wait_for_refresh_third_column()
    if get_current_chain_subject(web_obj) != title:
        chain_info = title
        if web_obj.attach:
            chain_info += "attaches "
        if web_obj.text:
            chain_info += "text "
        if web_obj.contacts:
            chain_info += "contacts "
        if web_obj.inline:
            chain_info += "inlines "
        if web_obj.reply_to:
            chain_info += "reply_to "
        error_msg = "!!!!!Failed to open chain '{0}' with!!!!!".format(
            chain_info)
        TEST_REPORT += error_msg, "\n"
        print error_msg


def hang_tag(web_obj, href, tag_name):
    combo = "".join(("//div[@id='mo.mcl-col-1']//a[@href='{0}']".format(href),
        "//div[@class='row tags']/div/a"))
    web_obj.find_element(combo, click=True)
    tag = "".join(("//div[@id='mo.mcl-col-1']//a[@href='{0}']",
        "//div[@class='row tags']//span[@title='{1}']")).format(href, tag_name)
    web_obj.find_element(tag, click=True)


def unhang_tag(web_obj, href, tag_name):
    tag_number = check_tag(web_obj, href, tag_name)
    if not tag_number:
        return "have no hanged tag '{0}'".format(tag_name)
    tag = "".join(("//div[@id='mo.mcl-col-1']//a[@href='{0}']",
        "//div[@class='row tags']/a[{1}]/a")).format(href, tag_number)
    web_obj.find_element(tag, click=True)
    return "unhanged with tag '{0}'".format(tag_name)


def switch_star(web_obj, href):
    star = "".join(("//div[@id='mo.mcl-col-1']//a[@href='{0}']".format(href),
        "//span[@name='star']"))
    web_obj.find_element(star, click=True)


def chain_counter(web_obj, href):
    counter = "".join(("//div[@id='mo.mcl-col-1']",
        "//a[@href='{0}']//div[@class='counter']".format(href)))
    counter_obj = web_obj.find_element(counter)
    return counter_obj.text[1:-1]


def check_tag(web_obj, href, tag_name):
    counter = 0
    while True:
        counter += 1
        tag = "".join(("//div[@id='mo.mcl-col-1']//a[@href='{0}']",
            "//div[@class='row tags']/a[{1}]")).format(href, counter)
        try:
            tag_obj = web_obj.driver.find_element_by_xpath(tag)
            if tag_obj.text == tag_name:
                return counter
        except (NoSuchElementException, StaleElementReferenceException):
            return
