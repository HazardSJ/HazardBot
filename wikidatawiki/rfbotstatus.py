import mwparserfromhell
import pywikibot


pywikibot.config.family = "wikidata"
pywikibot.config.mylang = "wikidata"
site = pywikibot.Site()
site.login()


class RFBOTStatusBot(object):
    """Updates the RFBOT status page"""

    def __init__(self):
        self.rfbot_page = pywikibot.Page(site, "Wikidata:Requests for permissions/Bot")
        self.status_page = pywikibot.Page(site, self.rfbot_page.title() + "/Status")
        self.time_format = "%Y-%m-%d, %H:%M:%S"
        self.table = """\
{| class="wikitable sortable"
! Bot Name !! Request created !! Last editor !! Last edited
%s
|}
"""
        self.row = """\
|-
| [[%(link)s|%(request)s]] || %(creation_date)s || %(last_editor)s || %(last_edited)s\
"""

    def run(self):
        requests = list()
        prefix = self.rfbot_page.title() + "/"
        rfbot_code = mwparserfromhell.parse(self.rfbot_page.get())

        for template in rfbot_code.ifilter_templates():
            if template.name.lower().strip().replace("_", " ").startswith(prefix.lower()):
                if not ("header" in template.name.lower() or "status" in template.name.lower()):
                    requests.append(template.name.strip().split("/")[-1])

        rows = list()
        for request in requests:
            page = pywikibot.Page(site, prefix + request)
            if not page.exists():
                continue
            first_edit = page.oldest_revision
            last_edit = next(page.revisions(total=1))
            rows.append(self.row % {
                "link": page.title(),
                "request": request,
                "creation_date": first_edit.timestamp.strftime(self.time_format),
                "last_editor": last_edit.user,
                "last_edited": "[[Special:Diff/%s|%s]]" % (
                    last_edit.revid,
                    last_edit.timestamp.strftime(self.time_format)
                )
            })

        status = self.table % ("\n".join(rows))
        self.status_page.put(status, "[[Wikidata:Bots|Bot]]: Updating RFBOT status table")


def main():
    try:
        bot = RFBOTStatusBot()
        bot.run()
    finally:
        pywikibot.stopme()

if __name__ == "__main__":
    main()
