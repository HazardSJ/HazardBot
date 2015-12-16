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


class ResearchHelpBot(object):
    """Adds {{Research help}} to articles from specific WikiProjects"""

    def __init__(self):
        self.maximum_edits = 50  # Per-run based, will be divided equally among all WikiProjects.
        self.groups = {
            "MED": {
                "template": "{{Research help|Med}}",
                "categories": (
                    pywikibot.Category(site, "Category:All WikiProject Medicine articles"),
                )
            },
            "MIL": {
                "template": "{{Research help|Mil}}",
                "categories": (
                    pywikibot.Category(site, "Category:World War I task force articles"),
                    pywikibot.Category(site, "Category:World War II task force articles")
                )
            }
        }
        reflist_template = pywikibot.Page(site, "Template:Reflist")
        self._reflist_template_titles = self._get_titles(reflist_template)
        self.valid_headings = ["endnotes", "footnotes", "references", "works cited"]

    def _get_titles(self, template):
        """Gets a list of the lowercase titles of a template and its redirects"""
        titles = [template.title(withNamespace=False).lower()]
        for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
            titles.append(reference.title(withNamespace=False).lower())
        return list(set(titles))

    def get_best_section(self, code):
        """Finds the section of with the list of references"""
        for section in code.get_sections(levels=[2]):
            if section.filter_headings()[0].title.lower().strip() in self.valid_headings:
                # Check for <references /> without `group` parameter
                if "<references" in section:
                    if "<references group" in section:
                        continue
                    return section
                # Check for {{reflist}} without `group` parameter
                for template in section.ifilter_templates():
                    if template.name.lower().strip() in self._reflist_template_titles:
                        if template.has_param("group"):
                            continue
                        return section
        return None

    def insert_rh_template(self, rh_template, section):
        rh_template += "\n"
        # Insert before <references />
        if "<references" in section:
            section.replace("<references", "%s<references" % rh_template)
            return
        # Insert before {{reflist}}
        for template in section.ifilter_templates():
            if template.name.lower().strip() in self._reflist_template_titles:
                if not template.has_param("group"):
                    section.insert_before(template, rh_template)
                    return

    def run(self):
        for group in self.groups.values():
            edits = 0
            for category in group["categories"]:
                for talk in category.articles(namespaces=1):
                    if edits >= (self.maximum_edits // len(self.groups.keys())):
                        break

                    page = talk.toggleTalkPage()
                    try:
                        text = page.get()
                    except pywikibot.Error:
                        continue

                    # Skip if the template was already added. Thankfully, no redirects exist.
                    if "research help" in text.lower():
                        continue

                    code = mwparserfromhell.parse(text, skip_style_tags=True)

                    section = self.get_best_section(code)

                    if section is not None:
                        self.insert_rh_template(group["template"], section)
                    else:
                        continue

                    if text == code:
                        continue

                    try:
                        summary = "[[Wikipedia:Bots|Bot]]: Adding %s" % group["template"]
                        summary += "; please leave feedback/comments at [[Wikipedia talk:Research help]]"
                        page.put(code, summary)
                    except pywikibot.Error:
                        continue
                    else:
                        edits += 1

                if edits >= (self.maximum_edits // len(self.groups.keys())):
                    continue


if __name__ == "__main__":
    try:
        bot = ResearchHelpBot()
        bot.run()
    finally:
        pywikibot.stopme()
