# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import pywikibot
from HazardBot.multiple import substituter


def main():
    site = pywikibot.Site("wikidata", "wikidata")
    template = pywikibot.Page(site, "Template:Subst only")
    bot = substituter.SubstitutionBot(site, template)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
