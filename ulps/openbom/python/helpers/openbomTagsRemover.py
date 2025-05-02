import html
from re import sub
from html.parser import HTMLParser
from helpers import openbomLogger
logger = openbomLogger.getLogger('OpenBOMTagsRemover')


class ToTextHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')
        elif tag == 'li':
            self.__text.append('\n')

    def text(self):
        return ''.join(self.__text).strip()


def toTextHtml(text):
    if not text:
        logger.warn('toTextHtml: Text parameter is empty')
        return text
    try:
        text = html.unescape(text)
        parser = ToTextHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except Exception as ex:
        logger.error('toTextHtml: %s', ex)
        return text
