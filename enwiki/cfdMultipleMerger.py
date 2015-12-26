# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import re

import mwparserfromhell
import pywikibot

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
#site.login()


class CFDMultipleMergeBot(object):
    def __init__(self):
        self.getMerges()

    def getMerges(self):
        page = pywikibot.Page(site, "Wikipedia:Categories for discussion/Working/Manual")
        text = page.get()
        code = mwparserfromhell.parse(text)
        section = code.get_sections(
            levels=[2],
            matches="Multiple merge targets",
            include_headings=False
        )[0]
        self.merges = re.findall(
            "\[\[:Category:(.*?)\]\] to \[\[:Category:(.*?)\]\] and \[\[:Category:(.*?)\]\]",
            unicode(section)
        )

    def run(self):
        for merge in self.merges:
            source_cat = pywikibot.Category(site, merge[0])
            target_cat1 = pywikibot.Category(site, merge[1])
            target_cat2 = pywikibot.Category(site, merge[2])
            if not (source_cat.exists() and target_cat1.exists() and target_cat2.exists()):
                continue
            for page in source_cat.articles():
                if page.namespace() != 0:
                    continue
                text = page.get()
                page_cats = pywikibot.getCategoryLinks(text)
                if source_cat in page_cats:
                    page_cats.remove(source_cat)
                if not target_cat1 in page_cats:
                    page_cats.append(target_cat1)
                if not target_cat2 in page_cats:
                    page_cats.append(target_cat2)
                new_text = pywikibot.replaceCategoryLinks(text, page_cats)
                if text == new_text:
                    continue
                pywikibot.showDiff(text, new_text)
                page.put(
                    new_text,
                    "[[Wikipedia:Bots|Bot]]: Merging from %s to %s and %s per CFD outcome" % (
                        source_cat.title(asLink=True),
                        target_cat1.title(asLink=True),
                        target_cat2.title(asLink=True)
                    )
                )
                break

        
def main():
    bot = CFDMultipleMergeBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
