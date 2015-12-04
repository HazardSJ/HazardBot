#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

import pywikibot

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class AFDRemoveRelistedCatBot(object):
    """Removes Category:AfD debates relisted 3 or more times from closed AfDs"""

    def __init__(self):
        self.category = pywikibot.Category(site, "Category:AfD debates relisted 3 or more times")

    def page_generator(self):
        for page in self.category.articles():
            if not page.title().startswith("Wikipedia:Articles for deletion/"):
                continue
            if page.title().startswith("Wikipedia:Articles for deletion/Log/"):
                continue
            if not "xfd-closed" in page.get():
                continue
            yield page

    def run(self):
        for page in self.page_generator():
            try:
                pywikibot.output(page.title(asLink=True))
                page.change_category(self.category, None,
                                     "[[Wikipedia:Bots|Bot]]: Removing closed AfD from %s" % self.category.title(
                                         asLink=True))
            except pywikibot.Error:
                pywikibot.output("Could not remove the category from %s" % page.title())


if __name__ == "__main__":
    try:
        bot = AFDRemoveRelistedCatBot()
        bot.run()
    finally:
        pywikibot.stopme()
