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


class UserSandboxTemplateFixer(object):
    def __init__(self):
        self.user_sandbox_template = pywikibot.Page(site, "Template:User sandbox")
        self.user_sandbox_template_titles = self._get_titles(self.user_sandbox_template)
        self.sandbox_heading_template = pywikibot.Page(site, "Template:Sandbox heading")
        self.sandbox_heading_template_titles = self._get_titles(self.sandbox_heading_template)

    def _get_titles(self, template):
        """Gets a list of the lowercase titles of a template and its redirects"""
        titles = [template.title(withNamespace=False).lower()]
        for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
            titles.append(reference.title(withNamespace=False).lower())
        return list(set(titles))

    def has_user_sandbox_template(self, code):
        for template in code.ifilter_templates():
            if template.name.lower().strip() in self.user_sandbox_template_titles:
                return True
        return False

    def replace_first_sandbox_heading_template(self, code):
        for template in code.ifilter_templates():
            if template.name.lower().strip() in self.sandbox_heading_template_titles:
                template.name.replace(template.name.strip(), self.user_sandbox_template.title(withNamespace=False))
                break
        return code

    def remove_sandbox_heading_templates(self, code):
        for template in code.ifilter_templates():
            if template.name.lower().strip() in self.sandbox_heading_template_titles:
                code.remove(template)
        return code

    def run(self):
        for page in self.sandbox_heading_template.getReferences(onlyTemplateInclusion=True, namespaces=[2,3]):
            if page.title(withNamespace=False) == "Sandbox":
                continue

            try:
                pywikibot.output(page.title(asLink=True))
            except UnicodeEncodeError:
                pass

            try:
                text = page.get()
            except pywikibot.Error:
                continue
            else:
                code = mwparserfromhell.parse(text)

            if not self.has_user_sandbox_template(code):
                code = self.replace_first_sandbox_heading_template(code)
                replaced = True
            else:
                replaced = False

            code = self.remove_sandbox_heading_templates(code)

            if text != code:
                try:
                    if replaced:
                        summary = "Replacing standard sandbox template with %s"
                    else:
                        summary = "Removing standard sandbox template (%s is already present)"
                    page.put(
                        code,
                        "[[Wikipedia:Bots|Bot]]: %s" % (summary % self.user_sandbox_template.title(asLink=True))
                    )
                except pywikibot.Error:
                    continue

if __name__ == "__main__":
    try:
        bot = UserSandboxTemplateFixer()
        bot.run()
    finally:
        pywikibot.stopme()
