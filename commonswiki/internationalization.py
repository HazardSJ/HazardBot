#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import re
import mwparserfromhell
import pywikibot
from pywikibot import xmlreader


pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()

class InternationalizationBot(object):
    def __init__(self):
        self.dumpFile = "/public/datasets/public/commonswiki/20131006/commonswiki-20131006-pages-articles.xml.bz2"
        self.loadFileTranslations()

    def loadFileTranslations(self):
        print "Loading translations of the 'File' namespace ..."
        self.fileTranslations = list()
        for lang in pywikibot.Site("en", "wikipedia").family.langs:
            self.fileTranslations.append(
                pywikibot.Site(lang, "wikipedia").namespace(6).lower()
            )
        self.fileTranslations = list(set(self.fileTranslations))
        print "... translations loaded."
        
    def fixFileTranslations(self):
        text = unicode(self.code)
        galleries = re.findall(
            "<gallery>\s*(.*?)\s*</gallery>",
            text,
            re.I|re.S
        )
        for gallery in galleries:
            for line in gallery.splitlines():
                try:
                    namespace, other = line.split(":", 1)
                except ValueError:
                    continue
                if namespace.lower().strip() in ["file", "image"]:
                    continue
                elif namespace.lower().strip() in self.fileTranslations:
                    namespace = namespace.replace(namespace.strip(), "File")
                    newLine = ":".join([namespace, other])
                    text = text.replace(gallery, gallery.replace(line, newLine))
        self.code = mwparserfromhell.parse(text)

    def fixHeadings(self):
        for heading in self.code.ifilter_headings():
            headingTitle = heading.title.lower().strip()
            if "license information" == headingTitle \
            or "{{int:license}}" == headingTitle \
            or "licensing" == headingTitle:
                heading.title = " {{int:license-header}} "
            elif "original upload log" == headingTitle \
            or "file history" == headingTitle:
                heading.title = " {{original upload log}} "
            elif "summary" == headingTitle:
                heading.title = " {{int:filedesc}} "

    def fixParameters(self):
        for template in self.code.ifilter_templates():
            if template.name.lower().strip() == "information":
                for param in template.params:
                    if param.name.lower().strip() == "source":
                        if "own work" == param.value:
                            param.value = unicode(param.value).replace(
                                param.value.strip(),
                                "{{own}}"
                            )
                    elif param.name.lower().strip() == "permission":
                        if "see below" == param.value:
                            param.value = unicode(param.value).replace(
                                param.value.strip(),
                                ""
                            )

    def makeFixes(self, text):
        self.code = mwparserfromhell.parse(text)
        oldCode = self.code
        try:
            self.fixFileTranslations()
        except (Exception, pywikibot.Error), error:
            print "\nError: %s\n" % error
        try:
            self.fixHeadings()
        except (Exception, pywikibot.Error), error:
            print "\nError: %s\n" % error
        try:
            self.fixParameters()
        except (Exception, pywikibot.Error), error:
            print "\nError: %s\n" % error
        if oldCode == self.code:
            return False
        else:
            return True

    def generator(self):
        dump = xmlreader.XmlDump(self.dumpFile)
        gen = dump.parse()
        for page in gen:
            if not page.ns in ["0", "6"]:
                continue
            if self.makeFixes(page.text):
                yield page.title

    def run(self):
        for title in self.generator():
            print
            page = pywikibot.Page(site, title)
            try:
                print page.title()
            except (UnicodeDecodeError, UnicodeEncodeError):
                print "(page_title)"
            try:
                text = page.get()
            except (Exception, pywikibot.Error), error:
                print "\nError: %s\n" % error
                continue
            if self.makeFixes(text):
                pywikibot.showDiff(text, unicode(self.code))
                try:
                    page.put(
                        unicode(self.code),
                        comment="[[Commons:Bots|Bot]]: Applied fixes for [[Commons:Template i18n|internationalization support]]"
                    )
                except (Exception, pywikibot.Error), error:
                    print "\nError: %s\n" % error


def main():
    bot = InternationalizationBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
