#-*- coding:utf8 -*-
import sys
import os
import time
import tkMessageBox

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from pyvirtualdisplay import Display


def read_config():
    temp = []
    config_dict = {}
    read_next = True
    stripped = ', '
    with open("config") as config_file:
        for line in config_file:
            line = line.strip()
            if line and line[0] != "#":
                if read_next:
                    parts = line.partition("=")
                    key = parts[0].strip(stripped)
                    temp.append(parts[2].strip(stripped))
                else:
                    temp.append(line.strip(stripped))
                if line[-1] == ",":
                    read_next = False
                else:
                    read_next = True
                    config_dict.update({key: temp})
                    temp = []
    return config_dict


def helper(seq_len):
    a = [[True], [False]]
    for i in xrange(seq_len):
        temp = []
        length = len(a)
        for j in xrange(length):
            tmp1 = a[j][:]
            tmp2 = a[j][:]
            tmp1.append(True)
            tmp2.append(False)
            temp.append(tmp1)
            temp.append(tmp2)
        a = temp[:]
    return a


def time_formatter(time_lists):
    output = ""
    for t_list in time_lists:
        output += t_list.pop(0)
        average = sum(t_list) / len(t_list)
        output += "    Количество прогонов: {0}\n".format(len(t_list))
        output += "    Среднее время: {0:.2f}.\n".format(average)
        output += "    Минимальное время: {0:.2f}.\n".format(min(t_list))
        output += "    Максимальное время: {0:.2f}.\n".format(max(t_list))
    return output


class WebBrowser(object):

    def __init__(self, driver, mail_url):
        self.driver = driver
        self.mail_url = mail_url
        self.sign_in()

    def sign_in(self):
        print "LOGINING..."
        global TESTING_ON_KOMTET
        self.driver.get(self.mail_url)
        if GUI:
            self.driver.maximize_window()
        else:
            self.driver.set_window_size(1700, 1000)

        login = "//*[@id='sin_login']"
        try:
            self.driver.find_element_by_xpath(login)
        except NoSuchElementException:
            login = "//*[@id='username']"
            self.driver.find_element_by_xpath(login)
            TESTING_ON_KOMTET = True
        self.find_element(login, typing=LOGIN)

        if TESTING_ON_KOMTET:
            password = "//*[@id='password']"
        else:
            password = "//*[@id='sin_password']"
        self.find_element(password, typing=PASSWORD)

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
        print target_link
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


class DraftManager(WebBrowser):

    def __init__(self, driver, subject="chain", text=True, attach=True,
                 inline=True, contacts=True, reply_to=True):
        self.driver = driver
        self.subject = subject
        self.text_flag = text
        self.attach_flag = attach
        self.inline_flag = inline
        self.reply_to_flag = reply_to
        self.contacts_flag = contacts
        self.cc = CC
        self.bcc = BCC
        self.reply_to = REPLY_TO
        self.counter = 0
        self.draft_list = set()

    def form_inline(self):
        print "Forming inlines..."
        inline_js = "".join(("$('#momail .panel .composer_form .mceEditor ",
            ".mceButton.mce_upload > input[type=file]')",
            ".css({width: '1px', height: '1px', opacity: 1})"))
        self.driver.execute_script(inline_js)
        attach_inline = "".join(("//a[@title='Paste images']",
            "//input[@type='file']"))
        for inline in INLINES:
            inline = unicode(inline, "utf-8")
            self.find_element(attach_inline, typing=inline)
        print "Inline attachments formed"

    def form_text(self, number_of_letter):
        print "Forming text..."
        self.switch_to_message_body()
        letter_text = ""    # Enter text of the letters here
        letter_text = "test_letter {0}\n{1}".format(number_of_letter,
            letter_text)
        body_text = "//body[@id='tinymce']"
        self.find_element(body_text, typing=letter_text)
        self.driver.switch_to_default_content()
        print "Letter text formed"

    def form_attach(self):
        print "Forming attachments..."
        attach = "".join(("//div[@class='wrapper attachments']//",
            "input[@type='file']"))
        for attachment in ATTACHMENTS:
            attachment = unicode(attachment, "utf-8")
            self.find_element(attach, typing=attachment)
        print "Attachments formed"

    def form_cc(self):
        print "Forming CC..."
        cc_link = "//div[@class='wrapper links']//a[@title='Add cc']"
        self.find_element(cc_link, click=True)
        cc = "//div[@class='wrapper cc']//input[@name='livesearch']"
        for contact in self.cc:
            self.find_element(cc, typing=contact + "\n")
        print "CC formed"

    def form_bcc(self):
        print "Forming BCC..."
        bcc_link = "//div[@class='wrapper links']//a[@title='Add bcc']"
        self.find_element(bcc_link, click=True)

        bcc = "//div[@class='wrapper bcc']//input[@name='livesearch']"
        for contact in self.bcc:
            self.find_element(bcc, typing=contact + "\n")
        print "BCC formed"

    def form_reply_to(self):
        print "Forming reply-to..."
        field = "//div[@class='context_menu_wrapper composer_wrapper']"
        self.find_element(field, hover=True)
        gear = "//div[@class='context_menu_wrapper composer_wrapper']/div/i"
        self.find_element(gear, click=True)

        reply_to = "//div[@class='subnav drop_left']//span[@action='reply_to']"
        self.find_element(reply_to, click=True)

        reply_to = "".join(("//div[@class='wrapper reply_to']",
            "//input[@name='livesearch']"))
        for contact in self.reply_to:
            self.find_element(reply_to, typing=contact + "\n")
        print "Reply-to formed"

    def form_to(self, email):
        print "Forming to..."
        to_input = "//div[@class='wrapper to']//input[@name='livesearch']"
        self.find_element(to_input, typing=email + "\n")
        print "To formed"

    def form_subject(self, chain_number):
        print "Forming subject..."
        subject = "//div[@class='wrapper subject']/div"
        subject_text = "{0}{1}".format(self.subject, chain_number)
        self.find_element(subject, typing=subject_text)
        print "Subject formed"

    def create_draft(self, email, number_of_letter=None):
        print "-----Forming draft..."
        if number_of_letter is None:
            number_of_letter = ""
            chain_number = ""
        else:
            chain_number = " {0}".format(self.counter)
            number_of_letter += 1
        compose_button = "".join(("//div[@id='mo.mcl-col-0']",
            "//i[@title='Compose mail...']"))
        self.find_element(compose_button, click=True)
        form = "//form[@class='composer_form']"
        self.find_element(form)

        self.form_to(email)
        self.form_subject(chain_number)
        if self.reply_to_flag:
            self.form_reply_to()
        if self.attach_flag:
            self.form_attach()
        if self.text_flag:
            self.form_text(number_of_letter)
        if self.contacts_flag:
            self.form_cc()
            self.form_bcc()
        if self.inline_flag:
            self.form_inline()

        save = "//div[@id='mo.mcl-col-2']//a[@class='button save']"
        self.find_element(save, click=True)
        self.wait_for_update()
        subject = "{0}{1}".format(self.subject, chain_number)
        print "-----Draft {0} created in chain '{1}{2}'.".format(
            number_of_letter, self.subject, chain_number)
        self.draft_list.add(subject)
        return (number_of_letter, subject)

    def create_drafts_chain(self, email, draft_count=3):
        self.counter += 1
        for increment in xrange(draft_count):
            self.create_draft(email, increment)
        subject = "{0} {1}".format(self.subject, self.counter)
        print "Draft-chain '{0}' formed.".format(subject)

    def change_chain_subject(self, chain_name):
        self.subject = chain_name
        self.counter = 0

    def change_attachment_flag(self, flag=None):
        self.attach_flag = not self.attach_flag if flag is None else flag

    def change_text_flag(self, flag=None):
        self.text_flag = not self.text_flag if flag is None else flag

    def change_contacts_flag(self, flag=None):
        self.contacts_flag = not self.contacts_flag if flag is None else flag

    def change_reply_to_flag(self, flag=None):
        self.reply_to_flag = not self.reply_to_flag if flag is None else flag

    def change_inline_flag(self, flag=None):
        self.inline_flag = not self.inline_flag if flag is None else flag

    def null_draft_list(self):
        self.draft_list = set()


class SendingManager(DraftManager):

    def __init__(self, driver, subject="chain", text=True, attach=True,
                 inline=True, contacts=True, reply_to=True):
        DraftManager.__init__(self, driver, subject="chain", text=text,
            attach=attach, inline=inline, contacts=contacts, reply_to=reply_to)
        self.driver = driver
        self.counter = 0
        self.sent_list = set()

    def send_letter(self, email, number_of_letter=None):
        print "-----Sending letter ..."
        number_of_letter, subject = self.create_draft(email,
            number_of_letter)

        send_button = "//div[@id='mo.mcl-col-2']//a[@class='button send']"
        self.find_element(send_button, click=True)
        self.wait_for_sending()
        print "-----Letter {0} sent in chain '{1}'.".format(number_of_letter,
            subject)
        self.sent_list.add(subject)

    def send_chain(self, email, letter_count=3):
        self.counter += 1
        for increment in xrange(letter_count):
            self.send_letter(email, increment)
        subject = "{0} {1}".format(self.subject, self.counter)
        print "Chain '{0}' formed.".format(subject)

    def send_complex_chains(self, email, number_of_chains, letter_count=3):
        for i in xrange(number_of_chains):
            self.send_chain(email, letter_count)

    def null_sent_list(self):
        self.sent_list = set()


# ===============TagManager====================================================
def get_tag_path(web_obj, tag_name):
    counter = 0
    while True:
        counter += 1
        tag = "".join(("//div[@id='mo.mcl-col-0']//div[@class='content']/div",
            "/div[{0}]".format(counter)))
        if counter > len(SYSTEM_TAGS):
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


# ============Second column controls===========================================
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
# =============================================================================


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
        error_msg = "!!!!!Failed to open chain '{0}' with!!!!!".format(chain_info)
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
# =============================================================================


# =============Third column chain operations===================================
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
# =============================================================================


# ================Test sets====================================================
def multiple_draft_test(web_obj):
    print "\n=====BEGIN MULTIPLE DRAFT TESTING====="
    msg = "!!!!!Multiple draft test failed!!!!!"
    try:
        select_tag(web_obj, "drafts")
        variants = helper(3)
        for variant in variants:
            web_obj.change_attachment_flag(variant[0])
            web_obj.change_text_flag(variant[1])
            web_obj.change_contacts_flag(variant[2])
            web_obj.change_inline_flag(variant[3])
            web_obj.create_drafts_chain(DESTINATION, 1)
        refresh_button(web_obj)
        operate_chain_by_subject(web_obj, web_obj.draft_list, "open_chain")
        msg = "=====Multiple draft test passed successfully====="
        clear_context(test_obj, ["sent"])
    finally:
        print msg


def single_draft_test(web_obj):
    print "\n=====BEGIN SINGLE DRAFT TESTING====="
    msg = "!!!!!Single draft test failed!!!!!"
    try:
        select_tag(web_obj, "drafts")
        web_obj.create_draft(DESTINATION)
        refresh_button(web_obj)
        operate_chain_by_subject(web_obj, web_obj.draft_list, "open_chain")
        msg = "=====Single draft test passed successfully====="
        clear_context(test_obj, ["drafts"])
    finally:
        print msg


def clear_context(web_obj, context_list):
    print "\n=====CLEANING MAILBOX====="
    msg = "!!!!!Cleaning failed!!!!!"
    try:
        for context in context_list:
            select_tag(web_obj, context)
            chains_checkbox(web_obj, "all")
            trash_button(web_obj)
        select_tag(web_obj, "trash")
        empty_trash_button(web_obj)
        web_obj.wait_for_refresh_second_column()
        msg = "=====Mailbox cleaned successfully====="
    finally:
        print msg


def fast_chain_test(web_obj):
    print "\n=====BEGIN FAST CHAIN TESTING====="
    msg = "!!!!!Fast chain test failed!!!!!"
    try:
        select_tag(web_obj, "sent")
        web_obj.change_text_flag(True)
        web_obj.send_chain(DESTINATION, 5)
        refresh_button(web_obj)
        operate_chain_by_subject(web_obj, web_obj.sent_list, "open_chain")
        msg = "=====Fast chain test passed successfully====="
        clear_context(test_obj, ["sent"])
    finally:
        print msg


def single_letter_test(web_obj):
    print "\n=====BEGIN SINGLE LETTER TESTING====="
    msg = "!!!!!Single letter test failed!!!!!"
    try:
        select_tag(web_obj, "sent")
        web_obj.send_letter(DESTINATION)
        refresh_button(web_obj)
        operate_chain_by_subject(web_obj, web_obj.sent_list, "open_chain")
        msg = "=====Single letter test passed successfully====="
        clear_context(test_obj, ["sent"])
    finally:
        print msg


def multiple_sending_test(web_obj):
    print "\n=====BEGIN MULTIPLE SENDING TEST====="
    msg = "!!!!!Multiple sending test failed!!!!!"
    try:
        variants = helper(3)
        select_tag(web_obj, "sent")
        for variant in variants:
            web_obj.change_attachment_flag(variant[0])
            web_obj.change_text_flag(variant[1])
            web_obj.change_contacts_flag(variant[2])
            web_obj.change_inline_flag(variant[3])
            web_obj.send_chain(DESTINATION, 1)
        refresh_button(web_obj)
        operate_chain_by_subject(web_obj, web_obj.sent_list, "open_chain")
        msg = "=====Multiple sending test passed successfully====="
        clear_context(test_obj, ["sent"])
    finally:
        print msg


def complex_tag_test(web_obj):
    print "\n=====BEGIN COMPLEX TAG TESTING====="
    msg = "!!!!!Complex tag test failed!!!!!"
    try:
        for tag in SYSTEM_TAGS:
            select_tag(web_obj, tag)
        select_tag(web_obj, "sent")
        web_obj.send_complex_chains(DESTINATION, len(TEST_TAGS), 1)
        chains_list = list(web_obj.sent_list)
        select_tag(web_obj, "sent")
        for i in xrange(len(chains_list)):
            create_tag(web_obj, TEST_TAGS[i])
            operate_chain_by_subject(web_obj, [chains_list[i]], "hang_tag",
                TEST_TAGS[i])
            web_obj.wait_for_update()
            if not operate_chain_by_subject(web_obj, [chains_list[i]],
                                            "check_tag", TEST_TAGS[i]):
                raise Exception
        print "All tags hanged right."

        for i in xrange(len(TEST_TAGS)):
            select_tag(web_obj, TEST_TAGS[i])
            operate_chain_by_subject(web_obj, [chains_list[i]],
                "open_chain")
        # дописать проверку тега в 3 столбце
        for i in xrange(len(TEST_TAGS)):
            edit_tag(web_obj, TEST_TAGS[i], TEST_TAGS[i] + "_new")
            select_tag(web_obj, TEST_TAGS[i] + "_new")
            operate_chain_by_subject(web_obj, [chains_list[i]],
                "open_chain")
            TEST_TAGS[i] = TEST_TAGS[i] + "_new"

        select_tag(web_obj, "sent")
        for i in xrange(len(chains_list)):
            if not operate_chain_by_subject(web_obj, [chains_list[i]],
                                            "check_tag", TEST_TAGS[i]):
                raise Exception
        print "All tags hanged right."

        for i in xrange(len(chains_list)):
            operate_chain_by_subject(web_obj, [chains_list[i]],
                "unhang_tag", TEST_TAGS[i])
        web_obj.wait_for_update()
        print "All tags unhanged right."

        for i in xrange(len(TEST_TAGS)):
            delete_tag(web_obj, TEST_TAGS[i])
        msg = "=====Complex tag test passed successfully====="
        clear_context(test_obj, ["sent"])
    finally:
        print msg


def simple_tag_test(web_obj):
    print "\n=====BEGIN SIMPLE TAG TESTING====="
    msg = "!!!!!Simple tag test failed!!!!!"
    try:
        for tag in TEST_TAGS:
            create_tag(web_obj, tag)
            select_tag(web_obj, tag)
            edit_tag(web_obj, tag, tag + "_new")
            select_tag(web_obj, tag + "_new")
            delete_tag(web_obj, tag + "_new")
        msg = "=====Simple tag test passed successfully====="
    finally:
        print msg
# =============================================================================


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
        test_obj = WebBrowser(webdriver.Chrome(CHROMEDRIVER_PATH), MAIL_URL)
    elif BROWSER == "firefox":
        test_obj = WebBrowser(webdriver.Firefox(), MAIL_URL)

    send_obj_t = SendingManager(test_obj.driver, attach=True, text=True,
                              contacts=True, inline=True, reply_to=True)
    send_obj_f = SendingManager(test_obj.driver, attach=False, text=False,
                              contacts=False, inline=False, reply_to=False)
    draft_obj = DraftManager(test_obj.driver, attach=True, text=True,
                             contacts=True, inline=True, reply_to=True)

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
