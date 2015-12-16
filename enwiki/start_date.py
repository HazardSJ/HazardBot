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
site.login()


class StartDateRemover(object):
    """Removes {{start date}} from {{singles}} and AltTitle= in {{episode list}}"""

    def __init__(self):
        self.start_date_template = pywikibot.Page(site, "Template:Start date")
        self.start_date_template_titles = self._get_titles(self.start_date_template)
        self.singles_template = pywikibot.Page(site, "Template:Singles")  # no redirects
        self.episode_list_template = pywikibot.Page(site, "Template:Episode list")  # no used redirects

    def _get_titles(self, template):
        """Gets a list of the lowercase titles of a template and its redirects"""
        titles = [template.title(withNamespace=False).lower()]
        for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
            titles.append(reference.title(withNamespace=False).lower())
        return list(set(titles))

    def _get_date(self, template, always_use_monthname=True):
        """Extracts the date from {{start date}} and returns it in text format"""
        if template.has_param(1) and template.has_param(2) and template.has_param(3):
            date = {
                "day": template.get(3).strip().lstrip("0"),
                "month": "{{subst:MONTHNAME|%s}}" % template.get(2).strip(),
                "year": template.get(1).strip()
            }
            if template.has_param("df"):
                return "%(day)s %(month)s %(year)s" % date
            else:
                return "%(month)s %(day)s, %(year)s" % date
        elif template.has_param(1) and template.has_param(2):
            if always_use_monthname:
                return "%(month)s %(year)s" % {
                    "month": "{{subst:MONTHNAME|%s}}" % template.get(2).strip(),
                    "year": template.get(1).strip()
                }
            else:
                month = template.get(2).value.strip()
                if month:
                    if int(month) < 10 and not month.startswith("0"):
                        month = "0" + month
                    return "%s %s" % (
                        template.get(1).value.strip(),
                        month
                    )
        elif template.has_param(1):
            return template.get(1).strip()
        else:
            return None

    def process_template(self, template):
        for page in template.getReferences(onlyTemplateInclusion=True, namespaces=0):
            try:
                text = page.get()
            except pywikibot.Error:
                continue
            else:
                code = mwparserfromhell.parse(text)

            for t in code.ifilter_templates():
                if t.name.lower().strip() == self.singles_template.title(withNamespace=False).lower():
                    for p in t.params:
                        if "date" in p.name:
                            for t2 in p.value.ifilter_templates():
                                if t2.name.lower().strip() in self.start_date_template_titles:
                                    date = self._get_date(t2, False)
                                    if date is not None:
                                        p.value.replace(
                                            t2,
                                            date
                                        )
                elif t.name.lower().strip() == self.episode_list_template.title(withNamespace=False).lower():
                    if t.has_param("AltDate"):
                        for t2 in t.get("AltDate").value.ifilter_templates():
                            if t2.name.lower().strip() in self.start_date_template_titles:
                                date = self._get_date(t2)
                                if date is not None:
                                    t.get("AltDate").value.replace(
                                        t2,
                                        date
                                    )
            if text != code:
                try:
                    page.put(code, "[[Wikipedia:Bots|Bot]]: Replacing {{[[Template:Start date|start date]]}} with date")
                except pywikibot.Error:
                    continue

    def run(self):
        self.process_template(self.singles_template)
        self.process_template(self.episode_list_template)


if __name__ == "__main__":
    try:
        bot = StartDateRemover()
        bot.run()
    finally:
        pywikibot.stopme()
