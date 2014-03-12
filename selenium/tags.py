#-*- coding:utf8 -*-
from time import sleep
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException


__all__ = ["get_tag_path", "tag_existance", "create_tag", "delete_tag",
           "edit_tag", "select_tag", "current_tag"]


def get_tag_path(web_obj, tag_name):
    counter = 0
    while True:
        counter += 1
        tag = "".join(("//div[@id='mo.mcl-col-0']//div[@class='content']/div",
            "/div[{0}]".format(counter)))
        if counter > len(web_obj.system_tags):
            pattern = tag + "/div[2]"
        else:
            pattern = tag + "/div"
        if web_obj.element_exists(pattern):
            pattern_attr = web_obj.find_element(pattern, attribute="data-name")
            if pattern_attr == tag_name:
                return tag
        else:
            break


def tag_existance(web_obj, tag_name):
    tag = "".join(("//div[@id='mo.mcl-col-0']//div[@class='content']",
        "//div[@data-name='{0}']".format(tag_name)))
    return web_obj.element_exists(tag)


def create_tag(web_obj, tag_name):
    print "Creating tag..."
    msg = "Tag '{0}' {1}."
    if tag_existance(web_obj, tag_name):
        print msg.format(tag_name, "already exists")
    else:
        tag = "//i[@class='momail ui button s26x26 text']"
        web_obj.find_element(tag, click=True)
        new_tag = "//div[@title='Enter name...']/div[2]"
        web_obj.find_element(new_tag, typing=tag_name + "\n")
        print msg.format(tag_name, "created successfully")
        sleep(1)


def delete_tag(web_obj, tag_name):
    print "Deleting tag..."
    msg = "Tag '{0}' {1}."
    if tag_existance(web_obj, tag_name):
        tag = get_tag_path(web_obj, tag_name)
        web_obj.find_element(tag, hover=True)
        web_obj.find_element(tag + "/div[1]/i[2]", click=True)
        print msg.format(tag_name, "deleted successfully")
    else:
        print msg.format(tag_name, "doesn't exist")
        sleep(1)


def edit_tag(web_obj, old_tag_name, new_tag_name):
    print "Editing tag..."
    if tag_existance(web_obj, new_tag_name):
        print "Tag '{0}' alredy exists. ".format(new_tag_name)
    else:
        if tag_existance(web_obj, old_tag_name):
            old_tag = get_tag_path(web_obj, old_tag_name)
            web_obj.find_element(old_tag, hover=True)
            web_obj.find_element(old_tag + "/div[1]/i[3]", click=True)
            web_obj.find_element(old_tag + "/div[2]",
                typing=new_tag_name + "\n")
            print "Tag '{0}' edited to '{1}' successfully.".format(
                old_tag_name, new_tag_name)
        else:
            print "Tag {0} doesn't exist.".format(old_tag_name)
        sleep(1)


def select_tag(web_obj, tag_name):
    print "Selecting tag..."
    msg = "Tag '{0}' {1}."
    if tag_existance(web_obj, tag_name):
        tag = get_tag_path(web_obj, tag_name)
        web_obj.find_element(tag, click=True)
        web_obj.wait_for_refresh_second_column()
        if current_tag(web_obj) == tag_name:
            print msg.format(tag_name, "selected successfully")
        else:
            print msg.format(tag_name, "was not selected")
    else:
        print msg.format(tag_name, "doesn't exist")


def current_tag(web_obj):
    system_tag = "".join(("//div[@id='mo.mcl-col-0']",
        "//div[@class='item momail icon system selected']/div"))
    tag = "".join(("//div[@id='mo.mcl-col-0']",
        "//div[@class='item momail icon selected']/div[2]"))
    try:
        tag_obj = web_obj.driver.find_element_by_xpath(system_tag)
    except (NoSuchElementException, StaleElementReferenceException):
        tag_obj = web_obj.driver.find_element_by_xpath(tag)
    current = tag_obj.get_attribute("data-name")
    return current
# =============================================================================
