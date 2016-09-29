"""
Extractor for the forum threads from the wiki list.
"""
from html.parser import HTMLParser
import re


class ListHTMLParser(HTMLParser):
    def __init__(self, format_list):
        # initialize the base class
        HTMLParser.__init__(self)
        self.format_list = format_list
        self.last_link = ''
        self.thread_list = []
        self.wiki_list_date = 0

    def error(self, message):
        print('ERROR:')

    def handle_starttag(self, tag, attrs):
        """
        Gets the last updated date of the wiki list and last possible thread link.
        :param tag:
        :param attrs:
        :return:
        """
        # a valid link must be inside of an 'a' tag
        if (tag != 'a') and (tag != 'span'):
            return
        for sub_tag, value in attrs:
            # if href is defined, set last_link
            if (sub_tag == "href") and (tag == 'a'):
                self.last_link = value
            if (sub_tag == "id") and (tag == 'span'):
                date = re.search(r"(\d\d).(\d\d).(\d\d\d\d)", value)
                if date is not None:
                    date = date.group()
                    self.wiki_list_date = int((date[-4:] + date[3:5] + date[:2]))

    def handle_endtag(self, tag):
        """
        Resets the last possible thread link if leaving the a tag.
        :param tag:
        :return:
        """
        # last_link is empty if outside of an 'a' tag
        if tag == 'a':
            self.last_link = ''

    def handle_data(self, data):
        """
        Checks for legal thread link and append them.
        :param data:
        :return:
        """
        # a valid link must be inside an 'a' tag and data must be a valid format
        # last_link is empty if outside of an 'a' tag
        if (data.lower() not in self.format_list) or (self.last_link == ''):
            return
        # cut the link, only the part after the hostname is needed
        self.last_link = self.last_link[25:]
        # only add unique links
        if self.last_link not in self.thread_list:
            self.thread_list.append(self.last_link)
