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

source = pywikibot.Page(site, "Template:Infobox company")
titles = [source.title(withNamespace=False).lower()]
for reference in source.getReferences(withTemplateInclusion=False, redirectsOnly=True):
    titles.append(reference.title(withNamespace=False).lower())
titles = list(set(titles))

for page in source.getReferences(onlyTemplateInclusion=True):
    text = page.get()
    code = mwparserfromhell.parse(text)
    for template in code.ifilter_templates():
        if not template.name.lower().strip() in titles:
            continue
        if not template.has_param("slogan"):
            continue
        if template.has_param("caption"):
            continue
        template.get("slogan").name = unicode(template.get("slogan").name).replace("slogan", "caption")
    if text != unicode(code):
        try:
            page.put(
                unicode(code),
                comment="[[Wikipedia:Bots|Bot]]: Replacing the depreciated parameter |slogan= with |caption= in {{infobox company}}"
            )
        except:
            pass

pywikibot.stopme()
