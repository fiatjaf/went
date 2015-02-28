# -*- encoding: utf-8 -*-

import re
import requests
import html2text
from bs4 import BeautifulSoup
from mf2py.parser import Parser

relwebmentionregex = re.compile('''<([^>]+)>; rel=["'](http://)?webmention(\.org/?)?["']''')

def url_in_source(url, source):
    soup = BeautifulSoup(source)
    return soup.find('a', attrs={'href': url})
    return soup.find('link', attrs={'href': url})

class Webmention(object):
    def __init__(self, url=None, source=None, target=None):
        if url:
            source = requests.get(url).text
        if target:
            if not url_in_source(target, source):
                return None

        mf2 = Parser(doc=source).to_dict()
        for item in mf2['items']:
            if 'h-entry' in item['type']:
                entry = item
                try:
                    html = item['properties']['content'][0]['html']
                except IndexError:
                    try:
                        html = item['properties']['summary'][0]
                    except IndexError:
                        html = item['children'][0]['value']

                self.body = html2text.html2text(html) # this cleans the html in the body

                self.author = {}
                try:
                    self.author['name'] = item['properties'].get('author', [{'properties': {}}])[0]['properties'].get('name', [None])[0]
                    self.author['photo'] = item['properties'].get('author', [{'properties': {}}])[0]['properties'].get('photo', [None])[0]
                    self.author['url'] = item['properties'].get('author', [{'properties': {}}])[0]['properties'].get('url', [None])[0]
                except KeyError:
                    pass

                self.date = item['properties'].get('published', [None])[0]
                self.published = self.date

                self.url = item['properties'].get('url', [None])[0]
                self.name = item['properties'].get('name', [None])[0]
                self.summary = item['properties'].get('summary', [None])[0]

                # bridgy specifics
                try:
                    self.via = item['properties']['uid'][0].split(',')[0].split(':')[1]
                except (IndexError, KeyError):
                    self.via = None

                break
