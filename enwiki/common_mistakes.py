# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import re

import pywikibot
from pywikibot import xmlreader

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class CommonMistakesLister(object):
    """Updates lists of common mistakes for WikiProject Fix common mistakes"""

    def __init__(self):
        blacklist_page = pywikibot.Page(site, "User:Hazard-Bot/Common mistakes blacklist")
        self.blacklist = re.findall("\[\[(.*?)\]\]", blacklist_page.get())
        self.dump_file = "/public/dumps/public/enwiki/20151201/enwiki-20151201-pages-articles.xml.bz2"
        self.mistakes = {
            "a a": list(),
            "a an": list(),
            "a the": list(),
            "an a": list(),
            "an an": list(),
            "and and": list(),
            "are are": list(),
            "be be": list(),
            "by by": list(),
            "for for": list(),
            "from from": list(),
            "he he": list(),
            "in in": list(),
            "is is": list(),
            "it it": list(),
            "of of": list(),
            "she she": list(),
            "the the": list(),
            "this this": list(),
            "to to": list(),
            "was was": list(),
            "were were": list(),
            "when when": list(),
            "with with": list(),
        }

    def check_page(self, page):
        for mistake in self.mistakes:
            if " %s " % mistake in page.text and " %s " % mistake in pywikibot.Page(site, page.title).get():
                self.mistakes[mistake].append(page.title)

    def list_mistakes(self):
        for mistake in self.mistakes:
            if len(self.mistakes[mistake]) > 0:
                mistake_page = pywikibot.Page(site, "Wikipedia:WikiProject Fix common mistakes/%s" % mistake)
                text = "# [["
                text += "]]\n# [[".join(sorted(self.mistakes[mistake]))
                text += "]]"
                try:
                    mistake_page.put(
                        text,
                        "Bot: Updating the list of common mistakes from the %s dump" % self.dump_file.split("/")[5]
                    )
                except pywikibot.Error:
                    continue

    def run(self):
        dump = xmlreader.XmlDump(self.dump_file)
        for page in dump.parse():
            if page.ns == "0" and page.title not in self.blacklist:
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
