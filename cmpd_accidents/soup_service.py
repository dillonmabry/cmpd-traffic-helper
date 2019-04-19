"""
Module for parsing XML/HTML
"""
from bs4 import BeautifulSoup


class SoupService(object):
    """
    Soup/Parser service for XML/HTML
    Args:
        text: the text to parse
        parse_type: parser type (XML, HTML, etc.) for bs4
    """

    def __init__(self, text, parse_type):
        self.soup = BeautifulSoup(text, parse_type)

    def findAll(self, tag):
        """
        Find all elements from given tag
        Args:
            tag: tag to find
        """
        tags = self.soup.findAll(tag)
        return tags

    def get_text(self, tag):
        """
        Get text representation of item total from soup parse
        Args:
            item: the tag/item to get text from
        """
        items = [item.get_text() for item in self.soup.findAll(tag)]
        return items

    def get_json(self, items):
        """
        Convert list of soup items with tags to list of json/dictionaries
        Args:
            items: list of soup items to convert
        """
        jsonArray = []
        for item in items:
            json_obj = {}
            for tag in item:
                json_obj[tag.name] = tag.get_text()
            jsonArray.append(json_obj)
        return jsonArray
