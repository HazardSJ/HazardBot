from __future__ import unicode_literals

import re
import time

import mwparserfromhell
import pywikibot
from pywikibot.data.api import Request


pywikibot.config.family = "wikidata"
pywikibot.config.mylang = "wikidata"

site = pywikibot.Site()
site.login()


class RFDArchiverBot:

    def __init__(self):
        self.time_diff = float(0.5 * (60 * 60))
        self.current_time = time.gmtime()
        self.current_timestamp = time.mktime(self.current_time)
        rfd_title = "Wikidata:Requests for deletions"
        archive_title = "%s/Archive/%s" % (
            rfd_title, time.strftime("%Y/%m/%d", self.current_time))
        self.rfd_page = pywikibot.Page(site, rfd_title)
        self.archive_page = pywikibot.Page(site, archive_title)
        self.archive_header = "{{Archive|category=Archived requests for deletion}}"
        self.response_templates = {
            "done", "deleted", "not done", "not deleted", "didn't delete"
        }
        for template in self.response_templates.copy():
            self.response_templates |= set(template_redirects(template))
        self.archive_count = 0

    def process_requests(self):
        sections = self.rfd_code.get_sections(levels=[2])
        for section in sections:
            responded = False
            templates = [template.name.lower().strip() for template in section.ifilter_templates()]
            for response_template in self.response_templates:
                if response_template in templates:
                    responded = True
                    break
            if not responded:
                continue
            timestamps = re.findall(
                "\d{1,2}:\d{2},\s\d{1,2}\s\D{3,9}\s\d{4}\s\(UTC\)", section.__unicode__(), re.DOTALL
            )
            timestamps = sorted(
                [time.mktime(time.strptime(timestamp[:-6], "%H:%M, %d %B %Y")) for timestamp in timestamps]
            )
            try:
                ts = timestamps[-1]
            except IndexError:
                continue
            if (self.current_timestamp - ts) > self.time_diff:
                self.archive_code.append(section)
                while section:
                    self.rfd_code.remove(section.get(0))
                self.archive_count += 1

    def get_summary(self, is_archive=False):
        summary = "[[Wikidata:Bots|Bot]]: %s %i request%s %s %s" % (
            "Archived" if is_archive else "Archiving",
            self.archive_count,
            "" if self.archive_count == 1 else "s",
            "from" if is_archive else "to",
            self.rfd_page.title(asLink=True) if is_archive else self.archive_page.title(asLink=True)
        )
        if is_archive:
            return summary
        version = self.rfd_page.getVersionHistory(total=1)[0]
        user = version[2]
        params = {
            "action": "query",
            "list": "users",
            "ususers": user,
            "usprop": "groups"
        }
        user_groups = Request(**params).submit()["query"]["users"][0]["groups"]
        summary += " (last edit at %s by [[User:%s|]]%s%s" % (
            version[1],
            user,
            " (administrator)" if (not ("bot" in user_groups) and ("sysop" in user_groups)) else "",
            ": '%s'" % version[3] if version[3] else ""
        )
        return summary

    def run(self):
        rfd_text = self.rfd_page.get(force=True)
        if self.archive_page.exists():
            archive_text = self.archive_page.get()
        else:
            archive_text = self.archive_header
        self.rfd_code = mwparserfromhell.parser.Parser().parse(rfd_text, skip_style_tags=True)
        self.archive_code = mwparserfromhell.parser.Parser().parse(archive_text + "\n\n", skip_style_tags=True)
        self.process_requests()
        if not self.archive_count:
            pywikibot.output("There are no archivable requests.")
            return
        self.rfd_page.put(self.rfd_code, comment=self.get_summary())
        self.archive_page.put(self.archive_code, comment=self.get_summary(is_archive=True))


def template_redirects(template_title):
    template_ns = 10
    template = pywikibot.Page(site, template_title, template_ns)
    redirects = template.backlinks(filter_redirects=True)
    # TODO: Verify that redirects are from the template namespace.
    return (redirect.title(with_ns=False).lower() for redirect in redirects)


def main():
    bot = RFDArchiverBot()
    bot.run()


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
