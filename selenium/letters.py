#-*- coding:utf8 -*-
from browser import WebBrowser


DEFAULT_ADDRESS = "motmomtest@motmom.com"
DEFAULT_IMAGE = "http://www.python.org/images/python-logo.gif"


class DraftManager(WebBrowser):

    def __init__(self,
                 driver,
                 subject="chain",
                 text_flag=True,
                 attach_flag=True,
                 inline_flag=True,
                 contacts_flag=True,
                 reply_to_flag=True,
                 inlines=DEFAULT_IMAGE,
                 attachments=DEFAULT_IMAGE,
                 cc=DEFAULT_ADDRESS,
                 bcc=DEFAULT_ADDRESS,
                 reply_to=DEFAULT_ADDRESS
                 ):

        self.driver = driver
        self.subject = subject
        self.text_flag = text_flag
        self.attach_flag = attach_flag
        self.inline_flag = inline_flag
        self.reply_to_flag = reply_to_flag
        self.contacts_flag = contacts_flag
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.attachments = attachments
        self.inlines = inlines
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
        for inline in self.inlines:
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
        for attachment in self.attachments:
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

    def __init__(self,
                 driver,
                 subject="chain",
                 text_flag=True,
                 attach_flag=True,
                 inline_flag=True,
                 contacts_flag=True,
                 reply_to_flag=True,
                 inlines=DEFAULT_IMAGE,
                 attachments=DEFAULT_IMAGE,
                 cc=DEFAULT_ADDRESS,
                 bcc=DEFAULT_ADDRESS,
                 reply_to=DEFAULT_ADDRESS
                 ):

        DraftManager.__init__(self,
                              driver,
                              subject=subject,
                              text_flag=text_flag,
                              attach_flag=attach_flag,
                              inline_flag=inline_flag,
                              contacts_flag=contacts_flag,
                              reply_to_flag=reply_to_flag,
                              inlines=inlines,
                              attachments=inlines,
                              cc=cc,
                              bcc=bcc,
                              reply_to=reply_to
                              )
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
