# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import re

import mwparserfromhell
import pywikibot
from pywikibot import xmlreader

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class CommonMistakesLister(object):
    """Updates lists of common mistakes for WikiProject Fix common mistakes"""

    def __init__(self):
        self.dump_file = "/public/dumps/public/enwiki/20160407/enwiki-20160407-pages-articles.xml.bz2"
        self.mistakes = self.parse_config("Wikipedia:WikiProject Fix common mistakes/Scan configuration")
        self.whitelist = self.parse_whitelist("Wikipedia:WikiProject Fix common mistakes/Whitelisted pages")
        self.filter_tags = ["math", "pre", "score", "source", "syntaxhighlight"]

    def parse_config(self, title):
        mistakes = dict()
        page = pywikibot.Page(site, title)
        text = page.get()
        code = mwparserfromhell.parse(text)
        sections = code.get_sections(levels=[2])
        for section in sections:
            mistake = section.filter_headings()[0].title.strip()
            if mistake:
                pattern = r" %s " % mistake
                for line in section.strip().splitlines():
                    if line.startswith("*"):
                        exception = line[1:].strip()
                        if exception:
                            pattern = r"(?! %s )%s" % (exception, pattern)
                mistakes[mistake] = {
                    "regex": re.compile(pattern),
                    "pages": list()
                }
        return mistakes

    def parse_whitelist(self, title):
        page = pywikibot.Page(site, title)
        text = page.get()
        code = mwparserfromhell.parse(text)
        return [link.title.lower().strip() for link in code.ifilter_wikilinks()]

    def filter_text(self, text):
        # Strip the comments
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        # Strip file names
        text = re.sub(r"\[\[(?:File|Image):.*?(?:\|(.*?))?\]\]", lambda m: m.group(1) or "",
                      text, flags=re.DOTALL|re.IGNORECASE)
        # Strip some HTML-style tags
        for tag in self.filter_tags:
            text = re.sub(r"<%(tag)s.*?</%(tag)s>" % {"tag": tag}, "", text, flags=re.DOTALL|re.IGNORECASE)
        # And we're done here
        return text

    def check_page(self, page):
        for mistake in self.mistakes:
            if self.mistakes[mistake]["regex"].search(self.filter_text(page.text)):
                try:
                    text = pywikibot.Page(site, page.title).get()
                except pywikibot.Error:
                    return
                else:
                    if self.mistakes[mistake]["regex"].search(self.filter_text(page.text)):
                        self.mistakes[mistake]["pages"].append(page.title)

    def list_mistakes(self):
        for mistake in self.mistakes:
            page = pywikibot.Page(site, "Wikipedia:WikiProject Fix common mistakes/%s" % mistake)
            if len(self.mistakes[mistake]["pages"]) > 0:
                text = "# [["
                text += "]]\n# [[".join(sorted(self.mistakes[mistake]["pages"]))
                text += "]]"
            else:
                text = ""
            try:
                page.put(
                    text,
                    "Bot: Updating the list of common mistakes from the %s dump" % self.dump_file.split("/")[5]
                )
            except pywikibot.Error:
                continue

    def run(self):
        dump = xmlreader.XmlDump(self.dump_file)
        for page in dump.parse():
            if page.ns == "0" and page.title.lower() not in self.whitelist:
                self.check_page(page)
        self.list_mistakes()


def main():
    bot = CommonMistakesLister()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
