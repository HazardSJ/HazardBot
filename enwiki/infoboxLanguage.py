#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import mwparserfromhell
import pywikibot

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()

templates = [
    pywikibot.Page(site, "Template:Infobox language"),
    pywikibot.Page(site, "Template:Infobox language family")
]
titles = list()
for template in templates:
    titles.append(template.title(withNamespace=False).lower())
    for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
        titles.append(reference.title(withNamespace=False).lower())
titles = list(set(titles))

report = dict()
for template in templates:
    for page in template.getReferences(onlyTemplateInclusion=True):
        text = page.get()
        code = mwparserfromhell.parse(text)
        for template in code.ifilter_templates():
            if not template.name.lower().strip() in titles:
                continue
            parameters = [param.name for param in template.params]
            duplicates = list()
            for parameter in parameters:
                if (parameters.count(parameter) > 1) and not (parameter in duplicates):
                    duplicates.append(unicode(parameter))
            if duplicates:
                try:
                    report[page.title()]
                except KeyError:
                    report[page.title()] = {}
                finally:
                    report[page.title()][template.name.strip()] = ", ".join(duplicates)
                print report  # log in output file
                print

pywikibot.stopme()