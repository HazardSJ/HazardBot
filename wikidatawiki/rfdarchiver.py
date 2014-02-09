#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

from __future__ import unicode_literals
import re
import time
import mwparserfromhell
import pywikibot
from pywikibot.data.api import Request


pywikibot.config.family = "wikidata"
pywikibot.config.mylang = "wikidata"

site = pywikibot.Site()
site.login()


class RFDArchiverBot(object):
    def __init__(self):
        self.timeDiff = float(1 * (60 * 60))
        self.currentTime = time.gmtime()
        self.currentTimestamp = time.mktime(self.currentTime)
        rfdTitle = "Wikidata:Requests for deletions"
        archiveTitle = "%s/Archive/%s" % (rfdTitle, time.strftime("%Y/%m/%d", self.currentTime))
        self.rfdPage = pywikibot.Page(site, rfdTitle)
        self.archivePage = pywikibot.Page(site, archiveTitle)
        self.archiveHeader = "{{Archive|category=Archived requests for deletion}}"
        self.responseTemplates = ["done", "deleted", "not done", "not deleted", "didn't delete"]
        self.archiveCount = 0

    def processRequests(self):
        sections = self.rfdCode.get_sections(levels=[2])
        for section in sections:
            responded = False
            templates = [template.name.lower().strip() for template in section.filter_templates()]
            for responseTemplate in self.responseTemplates:
                if responseTemplate in templates:
                    responded = True
                    break
            if not responded:
                continue
            timestamps = re.findall(
                "\d{1,2}:\d{2},\s\d{1,2}\s\D{3,9}\s\d{4}\s\(UTC\)", unicode(section), re.DOTALL
            )
            timestamps = sorted(
                [time.mktime(time.strptime(timestamp[:-6], "%H:%M, %d %B %Y")) for timestamp in timestamps]
            )
            try:
                ts = timestamps[-1]
            except IndexError:
                continue
            if (self.currentTimestamp - ts) > self.timeDiff:
                self.archiveCode.append(section)
                while section:
                    self.rfdCode.remove(section.get(0))
                self.archiveCount += 1

    def getSummary(self, isArchive = False):
        summary = "[[Wikidata:Bots|Bot]]: %s %i request%s %s %s" % (
            "Archived" if isArchive else "Archiving",
            self.archiveCount,
            "" if self.archiveCount == 1 else "s",
            "from" if isArchive else "to",
            self.rfdPage.title(allowInterwiki = False, asLink = True) if isArchive else self.archivePage.title(allowInterwiki = False, asLink = True)
        )
        if isArchive:
            return summary
        version = self.rfdPage.getVersionHistory(total=1)[0]
        user = version[2]
        params = {
            "action": "query",
            "list": "users",
            "ususers": user,
            "usprop": "groups"
        }
        userGroups = Request(**params).submit()["query"]["users"][0]["groups"]
        summary += " (last edit at %s by [[User:%s|]]%s%s" % (
            version[1],
            user,
            " (administrator)" if (not ("bot" in userGroups) and ("sysop" in userGroups)) else "",
            ": '%s'" % version[3] if version[3] else ""
        )
        return summary

    def run(self):
        Request(action="purge", titles=self.rfdPage.title()).submit()
        rfdText = self.rfdPage.get()
        if self.archivePage.exists():
            archiveText = self.archivePage.get()
        else:
            archiveText = self.archiveHeader
        self.rfdCode = mwparserfromhell.parse(rfdText)
        self.archiveCode = mwparserfromhell.parse(archiveText + "\n\n")
        self.processRequests()
        if not self.archiveCount:
            print "There are no archivable requests."
            return
        self.rfdPage.put(unicode(self.rfdCode), comment = self.getSummary())
        self.archivePage.put(unicode(self.archiveCode), comment = self.getSummary(isArchive = True))

def main():
    bot = RFDArchiverBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
