# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

from __future__ import unicode_literals
import re

import mwparserfromhell
import pywikibot
from pywikibot import xmlreader

pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

pywikibot.config.maxthrottle = 20
pywikibot.config.put_throttle = 2

site = pywikibot.Site()
site.login()


class InternationalizationBot(object):
    def __init__(self):
        self.dump_file = "/public/dumps/public/commonswiki/20151201/commonswiki-20151201-stub-articles.xml.gz"
        self.load_file_translations()

    def load_file_translations(self):
        print("Loading translations of the 'File' namespace ...")
        self.file_translations = list()
        for lang in pywikibot.Site("en", "wikipedia").family.langs:
            self.file_translations.append(
                pywikibot.Site(lang, "wikipedia").namespace(6).lower()
            )
        self.file_translations = list(set(self.file_translations))
        print("... translations loaded.")
        
    def fix_file_translations(self):
        text = self.code.__unicode__()
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
                elif namespace.lower().strip() in self.file_translations:
                    namespace = namespace.replace(namespace.strip(), "File")
                    new_line = ":".join([namespace, other])
                    text = text.replace(gallery, gallery.replace(line, new_line))
        self.code = mwparserfromhell.parse(text)

    def fix_headings(self):
        for heading in self.code.ifilter_headings():
            heading_title = heading.title.lower().strip()
            if "license information" == heading_title \
                    or "{{int:license}}" == heading_title \
                    or "licensing" == heading_title:
                heading.title = " {{int:license-header}} "
            elif "original upload log" == heading_title \
                    or "file history" == heading_title:
                heading.title = " {{original upload log}} "
            elif "summary" == heading_title:
                heading.title = " {{int:filedesc}} "

    def fix_parameters(self):
        for template in self.code.ifilter_templates():
            if template.name.lower().strip() == "information":
                for param in template.params:
                    if param.name.lower().strip() == "source":
                        if param.value.lower().strip() == "own work":
                            param.value.replace(
                                param.value.strip(),
                                "{{own}}"
                            )
                        elif param.value.lower().strip() == "unknown":
                            param.value.replace(
                                param.value.strip(),
                                "{{unknown|1=source}}"
                            )
                    elif param.name.lower().strip() == "author":
                        if param.value.lower().strip() == "unknown":
                            param.value.replace(
                                param.value.strip(),
                                "{{unknown|1=author}}"
                            )
                    elif param.name.lower().strip() == "permission":
                        if param.value.lower().strip() == "see below":
                            param.value.replace(
                                param.value.strip(),
                                ""
                            )

    def make_fixes(self, text):
        self.code = mwparserfromhell.parse(text)
        old_code = self.code
        try:
            self.fix_file_translations()
        except (Exception, pywikibot.Error) as error:
            print("\nError: %s\n" % error)
        try:
            self.fix_headings()
        except (Exception, pywikibot.Error) as error:
            print("\nError: %s\n" % error)
        try:
            self.fix_parameters()
        except (Exception, pywikibot.Error) as error:
            print("\nError: %s\n" % error)
        if old_code == self.code:
            return False
        else:
            return True

    def generator(self):
        dump = xmlreader.XmlDump(self.dump_file)
        gen = dump.parse()
        for page in gen:
            if page.ns not in ("0", "6"):
                continue
            if self.make_fixes(page.text):
                yield page.title

    def run(self):
        for title in self.generator():
            print("\n")
            page = pywikibot.Page(site, title)
            try:
                print(page.title())
            except UnicodeError:
                print("(page_title)")
            try:
                text = page.get()
            except (Exception, pywikibot.Error) as error:
                print("\nError: %s\n" % error)
                continue
            else:
                if not page.exists():
                    print("\nError: The page does not exist.\n" % error)
                    continue
            if self.make_fixes(text):
                pywikibot.showDiff(text, self.code)
                try:
                    page.put(
                        self.code,
                        "[[Commons:Bots|Bot]]: Applied fixes for [[Commons:Template i18n|internationalization support]]"
                    )
                except (Exception, pywikibot.Error) as error:
                    try:
                        print("\nError: %s\n" % error)
                    except UnicodeError:
                        pass


def main():
    bot = InternationalizationBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
