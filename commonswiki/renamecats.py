#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

from __future__ import unicode_literals
from json import dumps
import re
import mwparserfromhell
import pywikibot
from pywikibot import catlib
from pywikibot.data.api import Request


pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()


class RenameCategoryBot(object):
    def __init__(self):
        self.doTaskPage = pywikibot.Page(site, "User:Hazard-Bot/DoTask/7")
        self.queuePage = pywikibot.Page(site, "User:CommonsDelinker/commands")

    def checkDoTaskPage(self):
        try:
            text = self.doTaskPage.get(force = True)
        except pywikibot.IsRedirectPage:
            raise Exception(
                "The 'do-task page' (%s) is a redirect." %
                    self.doTaskPage.title(asLink = True)
            )
        except pywikibot.NoPage:
            raise Exception(
                "The 'do-task page' (%s) does not exist." %
                    self.doTaskPage.title(asLink = True)
            )
        else:
            if text.strip().lower() == "true":
                return True
            else:
                raise Exception(
                    "The task has been disabled from the 'do-task page' (%s)." %
                        self.doTaskPage.title(asLink = True)
                )

    def copyCat(self):
        if self.newCat.exists() or not self.oldCat.exists():
            return
        authors = ", ".join(self.oldCat.contributingUsers())
        summary = "[[Commons:Bots|Bot]]: Renamed from %s; the authors were %s" % \
            (self.oldCat.title(asLink = True), authors)
        if len(summary) > 255:
            newCatTalk = self.newCat.toggleTalkPage()
            try:
                talkText = newCatTalk.get()
                talkText += "\n\n"
            except pywikibot.NoPage:
                talkText = ""
            finally:
                talkText += "== Authors ==\nThe authors of the original category page are:\n* [[User:%s]]\n~~~~" % \
                    "]]\n * [[User:".join(self.oldCat.contributingUsers())
                newCatTalk.put(
                    talkText,
                    comment = "[[Commons:Bots|Bot]]: Listifying authors of the original category page"
                )
        catText = self.oldCat.get()
        catCode = mwparserfromhell.parse(catText)
        templates = catCode.filter_templates()
        for template in templates:
            if template.name.lower().strip() == "move":
                catCode.remove(template)
        self.newCat.put(unicode(catCode), summary)

    def updateWikidata(self):
        itemOld = pywikibot.ItemPage.fromPage(self.oldCat)
        itemNew = pywikibot.ItemPage.fromPage(self.newCat)
        if itemNew.exists():
            itemNew.editclaim(31, 4167836)
            itemNew.editclaim(373, self.newCat.title(withNamespace=False))
            return
        elif itemOld.exists():
            itemOld.setSitelink(
                sitelink={"site": site.dbName(), "title": self.newCat.title()},
                summary="Wikimedia Commons category moved"
            )
        else:
            itemNew.setSitelink(
                sitelink={"site": site.dbName(), "title": self.newCat.title()},
                summary="Importing category from Wikimedia Commons"
            )
            itemNew.editclaim(31, 4167836)
            itemNew.editclaim(373, self.newCat.title(withNamespace=False))

    def run(self):
        queueText = self.queuePage.get(force = True)
        queueCode = mwparserfromhell.parse(queueText)
        templates = queueCode.filter_templates()
        #templateNames = [temp.name.lower().strip() for temp in templates]
        #if "stop" in templateNames:
        #    raise Exception(
        #        "The task has been disabled from the 'queue page' (%s)." %
        #            self.queuePage.title(asLink = True)
        #    )
        for template in templates:
            self.checkDoTaskPage()
            if not template.name.lower().strip() == "move cat":
                continue
            if template.has_param(1) and template.has_param(2):
                self.oldCat = catlib.Category(site, template.get(1).value)
                self.newCat = catlib.Category(site, template.get(2).value)
            if template.has_param("reason"):
                reason = template.get("reason").value.strip()
            elif template.has_param(3):
                reason = template.get(3).value.strip()
            else:
                reason = None
            pages = list()
            pages.extend(list(self.oldCat.articles()))
            pages.extend(list(self.oldCat.subcategories()))
            if not self.oldCat.exists():
                continue
            if not self.newCat.exists():
                self.copyCat()
            for page in pages:
                oldText = page.get()
                newText = pywikibot.replaceCategoryInPlace(oldText, self.oldCat, self.newCat)
                if oldText != newText:
                    page.put(
                        newText,
                        comment = "[[Commons:Bots|Bot]]: Replaced category %s with %s%s" % (
                            self.oldCat.title(asLink = True),
                            self.newCat.title(asLink = True),
                            " (given reason: '%s')" % reason if reason else ""
                        )
                    )
            self.updateWikidata()
            if self.oldCat.exists() and not (list(self.oldCat.articles()) or list(self.oldCat.subcategories())):
                oldCatText = self.oldCat.get().lower()
                if not (re.search("bad\s?name", oldCatText) or "redir" in oldCatText):
                    self.oldCat.put(
                        "{{Category redirect|%s}}" % self.newCat.title(withNamespace = False),
                        comment = "[[Commons:Bots|Bot]]: Redirected renamed category to %s%s" % (
                            self.newCat.title(asLink = True),
                            " (given reason: '%s')" % reason if reason else ""
                        )
                    )

def main():
    bot = RenameCategoryBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
