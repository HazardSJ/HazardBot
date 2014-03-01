#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/

from __future__ import unicode_literals
import re
import mwparserfromhell
import pywikibot


class DGO4Bot(object):
    def __init__(self):
        self.wikidata = pywikibot.Site("wikidata", "wikidata", interface="DataSite")
        self.wikipedia = pywikibot.Site("fr", "wikipedia")
        self.DGO4re = re.compile("^\d{5}-\D{3}-\d{4}-\d{2}$")
        self.property = "P1133"
    
    def getData(self):
        source = pywikibot.Page(self.wikipedia, "Modèle:Classé Wallonie")
        pages = source.getReferences(follow_redirects=False, onlyTemplateInclusion=True, namespaces=[0], content=True)
        for page in pages:
            text = page.get()
            code = mwparserfromhell.parser.Parser().parse(text, skip_style_tags=True)
            for template in code.ifilter_templates():
                if template.name.strip().lower() != source.title(withNamespace=False).lower():
                    continue
                if template.has_param(4):
                    DGO4 = template.get(4).value.strip()
                    if self.DGO4re.match(DGO4):
                        yield pywikibot.ItemPage.fromPage(page), DGO4
                break
    
    def run(self):
        for item, DGO4 in self.getData():
            if not item.exists():
                continue
            data = item.get()
            if not self.property in data["claims"].keys():
                claim = pywikibot.Claim(self.wikidata, self.property)
                claim.setTarget(DGO4)
                item.addClaim(claim)


def main():
    bot = DGO4Bot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()