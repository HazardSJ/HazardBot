# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import mwparserfromhell
import pywikibot

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()

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