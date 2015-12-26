# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


from __future__ import unicode_literals
import re
import mwparserfromhell
import pywikibot


pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()


category = pywikibot.Category(site, "Category:Sammlung Duncker")

for page in category.articles():
    try:
        text = page.get()
        code = mwparserfromhell.parse(text)
        for template in code.ifilter_templates():
            if template.name.lower().strip() == "information":
                if template.has_param("Date"):
                    template.get("Date").value.replace(
                        template.get("Date").value.strip(),
                        "{{other date|between|1857|1883}}"
                    )
                elif template.has_param("date"):
                    template.get("date").value.replace(
                        template.get("date").value.strip(),
                        "{{other date|between|1857|1883}}"
                    )
                break
        if text != unicode(code):
            pywikibot.showDiff(text, unicode(code))
            page.put(
                unicode(code),
                "[[Commons:Bots|Bot]]: Correcting date parameter in {{information}}" +
                " (see https://commons.wikimedia.org/wiki/?diff=115838570 for details)"
            )
    except:
        pywikibot.output("Error with %s" % page.title())
