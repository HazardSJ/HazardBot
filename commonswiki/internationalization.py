# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


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
        self.dump_file = "/public/dumps/public/commonswiki/20160203/commonswiki-20160203-pages-articles.xml.bz2"
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
            re.IGNORECASE | re.DOTALL
        )
        for gallery in galleries:
            for line in gallery.splitlines():
                try:
                    namespace, other = line.split(":", 1)
                except ValueError:
                    continue
                if namespace.lower().strip() in ("file", "image"):
                    continue
                elif namespace.lower().strip() in self.file_translations:
                    namespace = namespace.replace(namespace.strip(), "File")
                    new_line = ":".join([namespace, other])
                    text = text.replace(gallery, gallery.replace(line, new_line))
        self.code = mwparserfromhell.parse(text)

    def fix_headings(self):
        for heading in self.code.ifilter_headings():
            heading_title = heading.title.lower().strip()
            if heading_title in ("{{int:license}}", "license information", "licensing"):
                heading.title = " {{int:license-header}} "
            elif heading_title in ("file history", "original upload log"):
                heading.title = " {{original upload log}} "
            elif heading_title == "summary":
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
        self.code = mwparserfromhell.parse(text, skip_style_tags=True)
        old_code = self.code
        try:
            self.fix_file_translations()
        except Exception as error:
            print("\nError: %s\n" % error)
        try:
            self.fix_headings()
        except Exception as error:
            print("\nError: %s\n" % error)
        try:
            self.fix_parameters()
        except Exception as error:
            print("\nError: %s\n" % error)
        if old_code == self.code:
            return False
        else:
            return True

    def generator(self):
        dump = xmlreader.XmlDump(self.dump_file)
        gen = dump.parse()
        for page in gen:
            if page.isredirect:
                continue
            if page.ns not in ("0", "6"):
                continue
            if self.make_fixes(page.text):
                yield page.title

    def run(self):
        for title in self.generator():
            print("\n")
            page = pywikibot.Page(site, title)
            pywikibot.output(page.title())
            try:
                text = page.get()
            except pywikibot.Error as error:
                pywikibot.output("\nError: %s\n" % error)
                continue
            if self.make_fixes(text):
                pywikibot.showDiff(text, self.code)
                try:
                    page.put(
                        self.code,
                        "[[Commons:Bots|Bot]]: Applied fixes for [[Commons:Template i18n|internationalization support]]"
                    )
                except pywikibot.Error as error:
                    pywikibot.output("\nError: %s\n" % error)


def main():
    bot = InternationalizationBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
