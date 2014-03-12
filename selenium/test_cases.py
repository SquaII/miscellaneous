#-*- coding:utf8 -*-
from helpers import helper
from tags import *
from second_column import *


__all__ = ["multiple_draft_test", "single_draft_test", "clear_context",
           "fast_chain_test", "fast_chain_test", "single_letter_test",
           "multiple_sending_test", "complex_tag_test", "simple_tag_test"]


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
