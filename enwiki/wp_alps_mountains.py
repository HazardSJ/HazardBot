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
site.login()


class AlpsMountainsBot(object):
    def __init__(self):
        self.site = pywikibot.Site()
        wp_template = pywikibot.Page(site, "Template:WikiProject Mountains")
        shell_template = pywikibot.Page(site, "Template:WikiProject Mountains")
        self.wp_template_titles = self._get_titles(wp_template)
        self.shell_titles = self._get_titles(shell_template)
        self.added_template = mwparserfromhell.parse(
            "{{WikiProject Mountains|class=|importance=|alps=yes|alps-importance=}}")

    def _get_titles(self, template):
        """Gets a list of the lowercase titles of a template and its redirects"""
        titles = [template.title(withNamespace=False).lower()]
        for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
            titles.append(reference.title(withNamespace=False).lower())
        return list(set(titles))

    def run(self):
        category = pywikibot.Category(site, "Category:Mountains of the Alps")
        for page in category.articles():
            if page.isTalkPage():
                talk = page
            else:
                talk = page.toggleTalkPage()
            article = talk.toggleTalkPage()

            try:
                talk_text = talk.get()
            except pywikibot.exceptions.NoPage:
                talk_text = ""
            except pywikibot.exceptions.IsRedirectPage:
                continue

            talk_code = mwparserfromhell.parse(talk_text)
            found = False
            shell = None
            for template in talk_code.ifilter_templates():
                if template.name.lower().strip() in self.shell_titles:
                    shell = template
                if not template.name.lower().strip() in self.wp_template_titles:
                    continue
                found = True
                if not template.has_param("alps"):
                    template.add("alps", "yes")
                    if not template.has_param("alps-importance"):
                        template.add("alps-importance", "")
                if not template.has_param("alps-importance"):
                    if template.has_param("importance"):
                        template.add("alps-importance", template.get("importance").value)
            if not found:
                article_text = article.get()
                article_code = mwparserfromhell.parse(article_text)
                article_templates = [t.name.lower().strip() for t in article_code.ifilter_templates()]
                stub = False
                for temp in article_templates:
                    if "stub" in temp:
                        stub = True
                        break
                if stub:
                    self.added_template.filter_templates()[0].add("class", "stub")

                # If there is a WikiProjectBannerShell, use it.
                if shell is not None:
                    shell = mwparserfromhell.parse(shell)
                    shell = shell.nodes[0]
                    shell.get(1).value.append("\n" + str(self.added_template))
                else:
                    lead_section = talk_code.get_sections()[0]
                    lead_templates = lead_section.filter_templates()
                    if lead_templates:
                        before = None
                        after = None
                        for t in lead_templates:
                            n = t.name.lower().strip()
                            if "wikiproject" in n or "wp" in n:
                                after = t
                            if "toc" in n:
                                before = t
                                break
                        if before is not None:
                            lead_section.insert_before(before, str(self.added_template)+"\n")
                        elif after is not None:
                            lead_section.insert_after(after, "\n"+str(self.added_template))
                        else:
                            if not lead_section.endswith("\n"):
                                lead_section.append("\n")
                            lead_section.append(self.added_template)
                            lead_section.append("\n\n")
                    else:
                        lead_section.insert(0, str(self.added_template)+"\n\n")
                summary = "Added"
            else:
                summary = "Updated"

            if talk_text.strip() != talk_code:
                try:
                    print(talk.title())
                except UnicodeEncodeError:
                    pass
                pywikibot.showDiff(talk_text.strip(), talk_code.strip())
                talk.put(
                    talk_code,
                    "[[Wikipedia:Bots|Bot]]: %s {{WikiProject Mountains}} template " % summary +
                    "([[Wikipedia talk:WikiProject Mountains|discussion]])"
                )
            else:
                try:
                    print(talk.title() + " (no edits)")
                except UnicodeEncodeError:
                    pass


if __name__ == "__main__":
    try:
        bot = AlpsMountainsBot()
        bot.run()
    finally:
        pywikibot.stopme()
