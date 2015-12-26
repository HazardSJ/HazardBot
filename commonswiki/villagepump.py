# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import pywikibot
from datetime import datetime

pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()

page = pywikibot.Page(site, "Commons:Village pump")

date = datetime.strftime(datetime.utcnow(), "%B %d")

header = "\n\n= %s =" % date
altheader = "\n\n=%s=" % date

text = page.get()

params = {
    "action": "edit",
    "title": "Commons:Village pump",
    "appendtext": "\n\n= %s =" % date,
    "token": site.token(page, "edit"),
    "summary": "[[Commons:Bots|Bot]]: Adding today's section header",
    "bot": 1,
    "minor": 1
}


def checkDoTaskPage():
    doTaskPage = pywikibot.Page(site, "User:Hazard-Bot/DoTask/Villagepump")
    if not doTaskPage:
        print "Note: No do-task page has been configured."
        return True
    try:
       text = doTaskPage.get(force = True)
    except pywikibot.IsRedirectPage:
        raise Warning("The 'do-task page' (%s) is a redirect." % doTaskPage.title(asLink = True))
    except pywikibot.NoPage:
        raise Warning("The 'do-task page' (%s) does not exist." % doTaskPage.title(asLink = True))
    else:
        if text.strip().lower() == "true":
            return True
        else:
            raise Exception("The task has been disabled from the 'do-task page' (%s)."
                % doTaskPage.title(asLink = True)
            )


if __name__ == "__main__":
    try:
        checkDoTaskPage()
        if not ((header in text) or (altheader in text)):
            print "Adding header"
            print pywikibot.data.api.Request(**params).submit()
        else:
            print "Header already present"
    finally:
        pywikibot.stopme()
