from __future__ import unicode_literals

import sys

import mwparserfromhell
import pywikibot


class SubstitutionBot(object):
    """Finds templates that should be substituted and substitutes them as necessary"""

    def __init__(self, site, template_name):
        self.site = site
        self.site.login()
        self.source_template = pywikibot.Page(site, template_name)

    def _templates_generator(self):
        generator = self.source_template.getReferences(only_template_inclusion=True, namespaces=[10])
        for page in generator:
            template = page
            if template.title().endswith("/doc") and pywikibot.Page(self.site, template.title()[:-4]).exists():
                template = pywikibot.Page(self.site, template.title()[:-4])
            if template != self.source_template:
                yield template
            for redirect in template.getReferences(filter_redirects=True, with_template_inclusion=False):
                yield redirect

    def run(self):
        for template in self._templates_generator():
            title = template.title(with_ns=False).lower()
            for page in template.getReferences(only_template_inclusion=True):
                try:
                    text = page.get()
                except pywikibot.Error:
                    continue
                else:
                    code = mwparserfromhell.parse(text)
                for temp in code.ifilter_templates():
                    if temp.has_param("nosubst") or temp.has_param("demo"):
                        continue
                    replace = False
                    if temp.name.lower().strip() == title:
                        replace = True
                    if temp.name.lower().strip().startswith("template:") and temp.name.lower().strip()[9:] == title:
                        replace = True
                    if replace:
                        temp.name = "subst:%s" % template.title()
                        temp.add("subst", "subst:")
                if text != code:
                    pywikibot.showDiff(text, code)
                    try:
                        page.put(
                            code,
                            "Bot: Substituting {{%s}}" % template.title(as_link=True, allow_interwiki=False)
                        )
                    except pywikibot.exceptions.Error:
                        continue


def main():
    site = None
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
        if db_name == "commonswiki":
            site = pywikibot.Site("commons", "commons")
            template_name = "Template:Must be substituted"
        # elif db_name == "enwiki":
        #     site = pywikibot.Site("en", "wikipedia")
        #     template_name = "Template:Subst only"
        elif db_name == "wikidatawiki":
            site = pywikibot.Site("wikidata", "wikidata")
            template_name = "Template:Subst only"
    if site is None:
        raise Exception("Please specify a valid database name.")
    else:
        bot = SubstitutionBot(site, template_name)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
