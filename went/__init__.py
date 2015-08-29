# -*- encoding: utf-8 -*-

import re
import urlparse
import requests
import datetime
import html2text
from mapping import Mapping
from bs4 import BeautifulSoup
from mf2py.parser import Parser

relwebmentionregex = re.compile('''<([^>]+)>; rel=["'](http://)?webmention(\.org/?)?["']''')

def url_in_source(url, source):
    soup = BeautifulSoup(source)
    return soup.find('a', attrs={'href': url})
    return soup.find('link', attrs={'href': url})

size_limits = {
  'summary': 422,
  'name': 50
}

class NoContent(ValueError):
    pass

class Webmention(Mapping):
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
                except (IndexError, KeyError):
                    try:
                        html = item['properties']['summary'][0]
                    except (IndexError, KeyError):
                        try:
                            html = item['properties']['name'][0]
                        except (IndexError, KeyError):
                            try:
                                html = item['children'][0]['value']
                            except (IndexError, KeyError):
                                raise NoContent

                self.html = html
                self.body = html2text.html2text(html) # this cleans the html in the body

                self.author = Author()
                try:
                    self.author.name = item['properties'].get('author', [{'properties': {}}])[0]['properties'].get('name', [None])[0]

                    self.author.photo = item['properties'].get('author', [{'properties': {}}])[0]['properties'].get('photo', [None])[0]
                    if self.author.photo:
                        self.author.photo = urlparse.urljoin(source, self.author.photo)
                        if not requests.head(self.author.photo).ok:
                            self.author.photo = None

                    self.author.url = item['properties'].get('author', [{'properties': {}}])[0]['properties'].get('url', [None])[0]
                    if self.author.url:
                        self.author.url = urlparse.urljoin(source, self.author.url)

                except KeyError:
                    pass

                self.published = item['properties'].get('published', [None])[0]
                if self.published:
                    self.date = self.published
                else:
                    self.date = datetime.datetime.now().isoformat()

                self.url = item['properties'].get('url', [None])[0]
                if self.url:
                    self.url = urlparse.urljoin(source, self.url)
                else:
                    self.url = source

                self.name = item['properties'].get('name', [None])[0]
                self.summary = item['properties'].get('summary', [None])[0]

                # bridgy specifics
                try:
                    self.via = item['properties']['uid'][0].split(',')[0].split(':')[1]
                except (IndexError, KeyError):
                    self.via = None

                break

        else:
            return None

        for key, limit in size_limits.items():
            for d in (self.__dict__, self.author):
                if key in d and type(d[key]) in (unicode, str):
                    d[key] = d[key][:limit]

class Author(Mapping):
    def __init__(self):
        self.photo = None
        self.name = None
        self.url = None
