import pywikibot


pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class AFDRelistedNullEditor(object):
    """Makes a null edit to AfDs transcluded in the logs on [[Category:Relisted AfD debates]]"""

    def __init__(self):
        self.afd_prefix = "Wikipedia:Articles for deletion/"
        self.category = pywikibot.Category(site, "Category:Relisted AfD debates")

    def process_log(self, log):
        for page in log.itertemplates():
            if page.title().startswith(self.afd_prefix):
                try:
                    if self.category.title() in page.get():
                        page.touch()
                except pywikibot.Error:
                    pass

    def run(self):
        for page in self.category.articles():
            if page.title().startswith(self.afd_prefix + "Log/"):
                self.process_log(page)


if __name__ == "__main__":
    try:
        bot = AFDRelistedNullEditor()
        bot.run()
    finally:
        pywikibot.stopme()
