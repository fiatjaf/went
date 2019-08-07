import re
import urllib
import urlparse
import requests
import datetime
import html2text
from mapping import Mapping
from bs4 import BeautifulSoup
from mf2py.parser import Parser

relwebmentionregex = re.compile(
    """<([^>]+)>; rel=["'](http://)?webmention(\.org/?)?["']"""
)


def url_in_source(url, source):
    soup = BeautifulSoup(source)
    return soup.find("a", attrs={"href": url})
    return soup.find("link", attrs={"href": url})


size_limits = {"summary": 422, "name": 50}


class NoContent(ValueError):
    pass


class NoURLInSource(ValueError):
    pass


class Proceed(Exception):
    pass


class Webmention(Mapping):
    def __init__(self, url=None, source=None, target=None, alternative_targets=[]):
        if url:
            source = requests.get(url).text
        if target:
            # verifying if the webmention body contains links to the correct
            # targetted object.
            if not url_in_source(target, source):
                try:
                    # the webmention can sometimes be sent with a target that is different
                    # from the link it contains in its body, because the webmention sender
                    # agent could have followed redirects to determine the first (or maybe
                    # the second), in this case we try to replicate its behavior by also
                    # following redirects and testing again with the final url.
                    target_final_url = requests.head(target, allow_redirects=True).url
                    if not url_in_source(target_final_url, source):
                        raise Proceed
                except:
                    # another option, just for the sake of completeness, is to allow the
                    # user who is receiving the webmention to specify multiple urls he
                    # will accept as correct if we found them in the webmention source,
                    # who can imagine what kind of bizarre software this user has in his
                    # hands so that he accepts a multitude of different urls for each post?
                    for altt in alternative_targets:
                        if url_in_source(altt, source):
                            break
                    else:
                        raise NoURLInSource

        mf2author = None
        mf2 = Parser(doc=source).to_dict()
        for item in mf2["items"]:
            if "h-entry" in item["type"]:
                try:
                    html = item["properties"]["content"][0]["html"]
                except (IndexError, KeyError):
                    try:
                        html = item["properties"]["summary"][0]
                    except (IndexError, KeyError):
                        try:
                            html = item["properties"]["name"][0]
                        except (IndexError, KeyError):
                            try:
                                html = item["children"][0]["value"]
                            except (IndexError, KeyError):
                                raise NoContent

                self.html = html
                self.body = html2text.html2text(
                    html
                )  # this cleans the html in the body

                self.published = item["properties"].get("published", [None])[0]
                if self.published:
                    self.date = self.published
                else:
                    self.date = datetime.datetime.now().isoformat()

                self.url = item["properties"].get("url", [None])[0]
                if self.url:
                    self.url = urlparse.urljoin(source, self.url)
                else:
                    self.url = source

                self.name = item["properties"].get("name", [None])[0]
                self.summary = item["properties"].get("summary", [None])[0]

                # bridgy specifics
                try:
                    self.via = item["properties"]["uid"][0].split(",")[0].split(":")[1]
                except (IndexError, KeyError):
                    self.via = None

                if (
                    len(
                        item["properties"].get(
                            "like", item["properties"].get("like-of", [])
                        )
                    )
                    > 0
                ):
                    self.like = True
                else:
                    self.like = False

                # try to get author information inside the h-entry
                mf2author = item["properties"].get(
                    "author", item["properties"].get("h-card", None)
                )

                break

        # after breaking out of the h-entry, parse author
        self.author = Author()

        if mf2author:
            try:
                author_properties = mf2author[0]["properties"]
            except (IndexError, KeyError):
                author_properties = None
        else:
            # get author information from outside h-entry
            for item in mf2["items"]:
                if "h-card" in item["type"]:
                    try:
                        author_properties = item["properties"]
                    except KeyError:
                        author_properties = None

        if author_properties:
            try:
                self.author.name = author_properties.get("name", [None])[0]

                self.author.photo = author_properties.get("photo", [None])[0]
                if self.author.photo:
                    self.author.photo = urlparse.urljoin(source, self.author.photo)
                    if not requests.head(self.author.photo).ok:
                        self.author.photo = None

                self.author.url = author_properties.get("url", [None])[0]
                if self.author.url:
                    self.author.url = urlparse.urljoin(source, self.author.url)

            except KeyError:
                pass

        # apply field limits
        for key, limit in size_limits.items():
            for d in (self.__dict__, self.author.__dict__):
                if key in d and type(d[key]) == str:
                    d[key] = d[key][:limit]

        # modify url when webmention is a facebook like (so url is unique)
        if self.like:
            src = urlparse.urlparse(self.url)
            qs = urlparse.parse_qs(src.query)
            qs["likes"] = qs.get("likes", self.author.url)
            query = urllib.urlencode(qs)
            self.url = urlparse.urljoin(self.url, "?" + query)


class Author(Mapping):
    def __init__(self):
        self.photo = None
        self.name = None
        self.url = None
