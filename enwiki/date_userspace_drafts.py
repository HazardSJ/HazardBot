import mwparserfromhell
import pywikibot


pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class UserspaceDraftDater(object):
    """Dates pages in [[Category:Userspace drafts]] to organize them in subcategories"""

    def __init__(self):
        self.category = pywikibot.Category(site, "Category:Userspace drafts")
        self.template = pywikibot.Page(site, "Template:Userspace draft")
        self.template_titles = self._get_titles(self.template)

    def _get_titles(self, template):
        """Gets a list of the lowercase titles of a template and its redirects"""
        titles = [template.title(withNamespace=False).lower()]
        for reference in template.getReferences(withTemplateInclusion=False, redirectsOnly=True):
            titles.append(reference.title(withNamespace=False).lower())
        return list(set(titles))

    def ensure_category(self, title):
        """Ensures the category exists, unless it is empty"""
        category = pywikibot.Category(site, title)
        if not category.exists():
            if len(list(category.articles())) > 0:
                category.put(
                        "{{Monthly clean-up category}}",
                        "[[Wikipedia:Bots|Bot]]: Creating monthly clean-up category for %s" %
                            self.template.title(asLink=True)
                )

    def run(self):
        for page in self.category.articles(namespaces=2):
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

            date = page.oldest_revision["timestamp"].strftime("%B %Y")

            for template in code.ifilter_templates():
                if template.name.lower().strip() in self.template_titles:
                    template.add("date", date)
                    break

            if text != code:
                try:
                    page.put(code, "[[Wikipedia:Bots|Bot]]: Adding date to %s" % self.template.title(asLink=True))
                    self.ensure_category("Category:Userspace drafts from %s" % date)
                except pywikibot.Error:
                    continue


if __name__ == "__main__":
    try:
        bot = UserspaceDraftDater()
        bot.run()
    finally:
        pywikibot.stopme()
