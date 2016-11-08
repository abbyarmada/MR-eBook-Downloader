"""
Extractor for the ebook links from the forum threads.
Checks only the first post for an possible ebook link. (self.in_container > 1)
"""
from html.parser import HTMLParser
import re


class ThreadHTMLParser(HTMLParser):
    """
    Links stored in a dict:
    key = link
    value = (name, last updated time)
    """
    def __init__(self, path):
        # initialize the base class
        HTMLParser.__init__(self)
        self.path = path
        self.last_link = ''
        self.link_data_list = []
        self.in_posts = False  # if in post sector
        self.in_container = 0  # if in container sector
        self.in_edit_note_part = False  # if in edit sector
        self.in_em_tag = False  # if in edit date/ time tag
        self.time = 0

    def error(self, message):
        # print('ERROR in ' + self.path)  # debug proposes
        return

    def handle_comment(self, data):
        """
        Check if in an edit sector and counts the post.
        :param data:
        :return:
        """
        if not self.in_posts:
            return
        # set if in edit sector
        if data == ' edit note ':
            self.in_edit_note_part = True
        if data == ' / edit note ':
            self.in_edit_note_part = False
        # set if in a post
        if data == ' open content container ':
            self.in_container += 1
        if data == ' / close content container ':
            self.in_container += 1

    def handle_starttag(self, tag, attrs):
        """
        Check if in edit part or post sector and get the last possible ebook link too.
        :param tag:
        :param attrs:
        :return:
        """
        # set if in post sector
        if tag == 'div':
            for sub_tag, value in attrs:
                if (sub_tag == 'id') and (value == 'posts'):
                    self.in_posts = True
                if (sub_tag == 'id') and (value == 'lastpost'):
                    self.in_posts = False  # stop parser?

        if (self.in_container > 1) or (not self.in_posts):  # if not in post sector and if not in a post
            return

        # a valid link must be inside of an 'a' tag
        if tag == 'a':
            for sub_tag, value in attrs:
                # if href is defined, set last_link
                if sub_tag == 'href':
                    self.last_link = value

        if tag == 'em':
            self.in_em_tag = True

    def handle_endtag(self, tag):
        """
        Check if in edit part or post sector or if outside of an a tag, reset the last possible ebook link.
        :param tag:
        :return:
        """
        if (self.in_container > 1) or (not self.in_posts):  # if not in post sector and if not in a post
            return

        # a valid link must be inside of an 'a' tag
        if tag == 'a':
            self.last_link = ''

        if tag == 'em':
            self.in_em_tag = False

    def handle_data(self, data):
        """
        Check for legal ebook links and gets a possible edit time.
        :param data:
        :return:
        """
        if (self.in_container > 1) or (not self.in_posts):  # if not in post sector and if not in a post
            return

        # a valid link must be inside an 'a' tag and data must be a valid format
        # last_link is empty if outside of an 'a' tag
        if (self.last_link != '') and ('attachment' in self.last_link):
            self.last_link = re.search(r"attachmentid=(\d)*", self.last_link).group()[13:]
            self.link_data_list.append((self.last_link, data))

        if self.in_em_tag:  # test for possible edit tag
            cur_date = re.search(r"(\d\d)-(\d\d)-(\d\d\d\d)", data)
            cur_time = re.search(r"(\d\d):(\d\d)", data)
            cur_afternoon = re.search("PM", data)
            if cur_date is not None:
                cur_date = cur_date.group().replace('-', '')
                self.time = int((cur_date[4:] + cur_date[:2] + cur_date[2:-4])) * 10000
            if cur_time is not None:
                if cur_afternoon is not None:  # its PM
                    self.time = self.time + int(cur_time.group().replace(':', '')) + 1200
                else:
                    self.time += int(cur_time.group().replace(':', ''))
