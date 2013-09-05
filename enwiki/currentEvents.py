#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import pywikibot
from datetime import datetime, timedelta

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class CurrentEventsBot(object):
    def __init__(self):
        self.prefix = "Portal:Current events/"
        self.text = """\
{{Current events header|%(year)s|%(month)s|%(day)s}}
<!-- All news items below this line -->
* 
<!-- All news items above this line -->|}
"""

    def getDate(self):
        date = dict()
        tomorrow = datetime.utcnow() + timedelta(days=1)
        date["day"] = tomorrow.day
        date["year"] = tomorrow.year
        date["month"] = tomorrow.strftime("%m")
        date["monthname"] = tomorrow.strftime("%B")
        self.date = date

    def run(self):
        self.getDate()
        tomorrow = "%(year)s %(monthname)s %(day)s" % self.date
        page = pywikibot.Page(site, self.prefix + tomorrow)
        if page.exists():
            return
        page.put(self.text % self.date, "[[Wikipedia:Bots|Bot]]: Creating tomorrow's current events page")


def main():
    bot = CurrentEventsBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
