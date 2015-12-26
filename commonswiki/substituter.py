# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


from __future__ import unicode_literals

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators

pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()


class SubstitutionBot(object):
    """Find templates on Wikimedia Commons that include {{Must be substituted}} and make substitutions as necessary."""

    def __init__(self):
        self.source = pywikibot.Page(site, "Template:Must be substituted")

    def _templates_generator(self):
        generator = pagegenerators.NamespaceFilterPageGenerator(
            pagegenerators.ReferringPageGenerator(self.source, onlyTemplateInclusion=True),
            [10]
        )
        for page in generator:
            template = page
            if template.title().endswith("/doc") and pywikibot.Page(site, template.title()[:-4]).exists():
                template = pywikibot.Page(site, template.title()[:-4])
            yield template
            for redirect in template.getReferences(redirectsOnly=True, withTemplateInclusion=False):
                yield redirect

    def run(self):
        for template in self._templates_generator():
            title = template.title(withNamespace=False).lower()
            for page in pagegenerators.ReferringPageGenerator(template, onlyTemplateInclusion=True):
                text = page.get()
                code = mwparserfromhell.parse(text)
                for temp in code.ifilter_templates():
                    if temp.name.lower().strip() == title:
                        temp.name = "subst:%s" % template.title()
                if text != code:
                    pywikibot.showDiff(text, code)
                    page.put(
                        code,
                        "[[Commons:Bots|Bot]]: Substituting {{%s}}" % template.title(asLink=True)
                    )


if __name__ == "__main__":
    try:
        bot = SubstitutionBot()
        bot.run()
    finally:
        pywikibot.stopme()
