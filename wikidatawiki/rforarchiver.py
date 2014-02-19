#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


from datetime import datetime
import re
import mwparserfromhell
import pywikibot


pywikibot.config.family = "wikidata"
pywikibot.config.mylang = "wikidata"

site = pywikibot.Site()
site.login()


class RFORArchiverBot(object):
    def __init__(self):
        self.basePage = pywikibot.Page(site, "Wikidata:Requests for permissions")
        self.requestsPage = pywikibot.Page(site, self.basePage.title() + "/Other rights")
        self.archiveTitles = {
            "autopatrolled": self.basePage.title() + "/RfAutopatrol/%s",
            "confirmed": self.basePage.title() + "/RfConfirmed/%s",
            # "ipblock-exempt": self.basePage.title() + "",  # Not archived currently
            "propertycreator": self.basePage.title() + "/RfPropertyCreator/%s",
            "rollbacker": self.basePage.title() + "/RfRollback/%s"
        }
        self.closedRegex = "\n\{\{\s*(?:A(?:rchive)?|D(?:iscussion)?) ?top\|.*?\}\}.*?"
        self.closedRegex += "\{\{\s*(?:A(?:rchive)?|D(?:iscussion)?) ?bottom\}\}\n"
        self.archiveText = "{{Archive|category=Archived requests for permissions}}"
        self.archiveText += "\n__TOC__\n{{Discussion top}}\n\n"

        
    def run(self):
        text = self.requestsPage.get()
        code = mwparserfromhell.parse(text)
        for section in code.get_sections(levels=[2]):
            if "autopatrol" in section.filter_headings()[0].title.lower():
                group = "autopatrolled"
            elif "confirmed" in section.filter_headings()[0].title.lower():
                group = "confirmed"
            elif "property" in section.filter_headings()[0].title.lower():
                group = "propertycreator"
            elif "rollback" in section.filter_headings()[0].title.lower():
                group = "rollbacker"
            else:
                continue
            archivable = list()
            discussions = re.findall(self.closedRegex, unicode(section), re.I|re.S)
            for discussion in discussions:
                timestamps = re.findall(
                    "\d{1,2}:\d{2},\s\d{1,2}\s\D{3,9}\s\d{4}\s\(UTC\)", unicode(section)
                )
                timestamps = sorted(
                    [datetime.strptime(timestamp[:-6], "%H:%M, %d %B %Y") for timestamp in timestamps]
                )
                if (datetime.utcnow() - timestamps[-1]).days > 5:
                    archivable.append(discussion)
            if not archivable:
                continue
            for remove in archivable:
                code = mwparserfromhell.parse(
                    unicode(code).replace(remove, "")
                )
            archive = pywikibot.Page(
                site,
                self.archiveTitles[group] % datetime.utcnow().strftime("%B %Y")
            )
            if archive.exists():
                archiveText = archive.get() + "\n\n"
            else:
                archiveText = self.archiveText
            archiveCode = mwparserfromhell.parse(archiveText)
            for add in archivable:
                new = mwparserfromhell.parse(add)
                new.nodes = new.nodes[1:-2]
                append = unicode(new).strip() + "\n\n"
                if not append in archiveCode:
                    archiveCode.append(append)
            archive.put(
                unicode(archiveCode),
                "[[Wikidata:Bots|Bot]]: Archiving from %s" % self.requestsPage.title(asLink=True)
            )
        pywikibot.showDiff(text, unicode(code))
        if text != unicode(code):
            self.requestsPage.put(unicode(code), "[[Wikidata:Bots|Bot]]: Archived closed requests")


def main():
    bot = RFORArchiverBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
