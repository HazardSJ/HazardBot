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
        template = pywikibot.Page(site, "Template:WikiProject Mountains")
        self.template_titles = list()
        self.template_titles.append(template.title(withNamespace=False).lower())
        for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
            self.template_titles.append(reference.title(withNamespace=False).lower())
        self.template_titles = list(set(self.template_titles))
        self.added_template = mwparserfromhell.parse("{{WikiProject Mountains|class=|importance=|alps=yes|alps-importance=}}\n")
    
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
            for template in talk_code.ifilter_templates():
                if not template.name.lower().strip() in self.template_titles:
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
                talk_code.insert(0, self.added_template)
                summary = "Added"
            else:
                summary = "Updated"
            if talk_text != unicode(talk_code):
                print talk.title()
                pywikibot.showDiff(talk_text, unicode(talk_code))
                talk.put(unicode(talk_code), "[[Wikipedia:Bots|Bot]]: %s {{WikiProject Mountains}} template ([[Wikipedia talk:WikiProject Mountains|discussion]])" % summary)
            else:
                print talk.title() + " (no edits)"

if __name__ == "__main__":
    try:
        bot = AlpsMountainsBot()
        bot.run()
    finally:
        pywikibot.stopme()
