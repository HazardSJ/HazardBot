from datetime import datetime
import re

import mwparserfromhell
import pywikibot


pywikibot.config.family = "wikidata"
pywikibot.config.mylang = "wikidata"

site = pywikibot.Site()
site.login()


class RFORArchiverBot:
    """Archives closed requests on [[Wikidata:Requests for permissions/Other rights]]"""

    RESOLUTION_TEMPLATES = {"done", "not done", "notdone", "withdrawn"}

    def __init__(self):
        self.base_page = pywikibot.Page(site, "Wikidata:Requests for permissions")
        self.requests_page = pywikibot.Page(site, self.base_page.title() + "/Other rights")
        self.archive_titles = {
            "confirmed": self.base_page.title() + "/RfConfirmed/%B %Y",
            "event-organizer": self.base_page.title() + "/RfEventOrganizer/%Y",  # archived by the year
            "ipblock-exempt": self.base_page.title() + "/RfIPBE/%Y",  # archived by the year
            "propertycreator": self.base_page.title() + "/RfPropertyCreator/%B %Y",
            "rollbacker": self.base_page.title() + "/RfRollback/%B %Y"
        }
        self.closed_regex = "\n\{\{\s*(?:A(?:rchive)?|D(?:iscussion)?) ?top\|.*?\}\}.*?"
        self.closed_regex += "\{\{\s*(?:A(?:rchive)?|D(?:iscussion)?) ?bottom\}\}\n"
        self.archive_text = "{{Archive|category=Archived requests for permissions}}"
        self.archive_text += "\n__TOC__\n{{Discussion top}}"

    def run(self):
        text = self.requests_page.get()
        code = mwparserfromhell.parser.Parser().parse(text, skip_style_tags=True)
        for section in code.get_sections(levels=[2]):
            heading = section.filter_headings()[0].title.lower()
            if "confirmed" in heading:
                group = "confirmed"
            elif "event organizer" in heading:
                group = "event-organizer"
            elif "ipbe" in heading:
                group = "ipblock-exempt"
            elif "property" in heading:
                group = "propertycreator"
            elif "rollback" in heading:
                group = "rollbacker"
            else:
                continue
            archivable = []
            for discussion in section.get_sections(levels=[3]):
                for template in discussion.ifilter_templates():
                    if template.name.lower().strip() in self.RESOLUTION_TEMPLATES:
                        break  # Start processing this section.
                else:
                    continue  # Skip to next section.
                
                timestamps = re.findall(
                    "\d{1,2}:\d{2},\s\d{1,2}\s\D{3,9}\s\d{4}\s\(UTC\)", str(discussion)
                )
                timestamps = sorted(
                    datetime.strptime(timestamp[:-6], "%H:%M, %d %B %Y")
                    for timestamp in timestamps
                )
                if (datetime.utcnow() - timestamps[-1]).days >= 5:
                    archivable.append(discussion)
            if len(archivable) == 0:
                continue
            archive = pywikibot.Page(
                site,
                datetime.utcnow().strftime(self.archive_titles[group])
            )
            archive_text = archive.get() if archive.exists() else self.archive_text
            archive_code = mwparserfromhell.parse(archive_text)
            for add in archivable:
                append = add.strip()
                if append not in archive_code:
                    archive_code.append("\n\n" + append)
            for remove in archivable:
                code.remove(remove)
            archive.put(
                archive_code,
                "[[Wikidata:Bots|Bot]]: Archiving from %s" % self.requests_page.title(as_link=True)
            )
        pywikibot.showDiff(text, code)
        if text != code:
            self.requests_page.put(code, "[[Wikidata:Bots|Bot]]: Archived closed requests")


def main():
    bot = RFORArchiverBot()
    bot.run()


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
