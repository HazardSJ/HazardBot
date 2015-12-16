#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

import re

import pywikibot

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class AFDRelistedCatRemover(object):
    """Removes closed from relisted AfD categories"""

    def __init__(self):
        self.categories = [
            pywikibot.Category(site, "Category:AfD debates relisted 3 or more times"),
            pywikibot.Category(site, "Category:Relisted AfD debates")
        ]

    def page_generator(self, category):
        for page in category.articles():
            if not page.title().startswith("Wikipedia:Articles for deletion/"):
                continue
            if page.title().startswith("Wikipedia:Articles for deletion/Log/"):
                continue
            if "xfd-closed" not in page.get():
                continue
            yield page

    def remove(self, pattern, text):
        to_remove = list()
        for cat in self.categories:
            to_remove += re.findall(pattern % cat.title(), text)
        for c in set(to_remove):
                    text = text.replace(c, "")
        return text

    def run(self):
        for category in self.categories:
            pywikibot.output(category.title(asLink=True) + "\n")

            for page in self.page_generator(category):
                try:
                    pywikibot.output(page.title(asLink=True))
                except UnicodeEncodeError:
                    pass

                try:
                    text = page.get()
                except pywikibot.Error:
                    continue

                old_text = text
                text = self.remove("<noinclude>\[\[%s(?:\|.*?)?\]\]</noinclude>", text)
                text = self.remove("\[\[%s(?:\|.*?)?\]\]", text)

                if old_text == text:
                    continue

                try:
                    page.put(text, "[[Wikipedia:Bots|Bot]]: Removing closed AfD from %s" % category.title(asLink=True))
                except pywikibot.Error:
                    pywikibot.output("Could not remove the category from %s" % page.title())
            pywikibot.output("\n")


if __name__ == "__main__":
    try:
        bot = AFDRelistedCatRemover()
        bot.run()
    finally:
        pywikibot.stopme()
