# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


import pywikibot
from datetime import datetime, timedelta

pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"
site = pywikibot.Site()
site.login()


class SubCreatorBot(object):
    def __init__(self):
        self.getDate()
        self.subs = {
#            "currentevents": {
#                "title": "Portal:Current events/%(year)s %(monthname)s %(day)s",
#                "text": """\
#{{Current events header|%(year)s|%(month2)s|%(day)s}}
#<!-- All news items below this line -->
#* 
#<!-- All news items above this line -->|}
#"""
#            },
            "differentname": {
                "title":
                    "Category:Wikipedia files with a different name on Wikimedia Commons as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Wikipedia files with a different name on Wikimedia Commons starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
            "disputednonfree": {
                "title":
                    "Category:Disputed non-free Wikipedia files as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Disputed non-free images subcategory starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
            "missingpermission": {
                "title":
                    "Category:Wikipedia files missing permission as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Files missing permission subcategory starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
            "nononfreeuserationale": {
                "title":
                    "Category:Wikipedia files with no non-free use rationale as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Images with no fair use rationale subcat starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
            "orphanednonfreeuse": {
                "title":
                    "Category:Orphaned non-free use Wikipedia files as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Orphaned non-free use subcat starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
#             "possiblyunfree": {
#                 "title":
#                     "Category:Possibly unfree files from %(year)s %(monthname)s %(day)s",
#                 "text": """\
# {{subst:Possibly unfree files subcategory starter|%(year)s|%(monthname)s||%(day)s|MONTHNO=%(month2)s}}
# """
#             },
            "prod": {
                "title":
                    "Category:Proposed deletion as of %(day)s %(monthname)s %(year)s",
                "text": "{{subst:Prod subcategory starter|%(year)s|%(monthname)s||%(day)s}}"
            },
            "replaceablenonfreeuse": {
                "title":
                    "Category:Replaceable non-free use to be decided after %(day+7)s %(monthname+7)s %(year+7)s",
                "text": """\
{{subst:Replaceable non-free use images subcategory starter|%(year+7)s|%(monthname+7)s||%(day+7)s}}
"""
            },
            "rfd": {
                "title":
                    "Wikipedia:Redirects for discussion/Log/%(year)s %(monthname)s %(day)s",
                "text": """\
{{subst:RfD subpage starter|1=%(year)s|2=%(monthname)s|4=%(day)s|7=%(year-)s|8=%(monthname-)s|10=%(day-)s|13=%(year+)s|14=%(monthname+)s|16=%(day+)s}}
"""
            },
            "samename": {
                "title":
                    "Category:Wikipedia files with the same name on Wikimedia Commons as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Wikipedia files with the same name on Wikimedia Commons starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
            "unknowncopyright": {
                "title":
                    "Category:Wikipedia files with unknown copyright status as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Wikipedia files with unknown copyright status subcategory starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
            "unknownsource": {
                "title":
                    "Category:Wikipedia files with unknown source as of %(day)s %(monthname)s %(year)s",
                "text": [
                    """\
{{subst:Wikipedia files with unknown source subcategory starter|%(year)s|%(monthname)s||%(day)s}}
""",
                    """\
{{subst:Wikipedia files with unknown source subcategory starter nogallery|%(year)s|%(monthname)s||%(day)s|REVID=%(revid)s}}
"""
                ]
            },
            "uploadassistance": {
                "title":
                    "Category:Wikipedia files needing editor assistance at upload as of %(day)s %(monthname)s %(year)s",
                "text": """\
{{subst:Wikipedia files needing editor assistance at upload subcategory starter|%(year)s|%(monthname)s||%(day)s}}
"""
            },
        }

    def getDate(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        dayAfterTomorrow = tomorrow + timedelta(days=1)
        dayBeforeTomorrow = tomorrow - timedelta(days=1)
        weekAfterTomorrow = tomorrow + timedelta(days=7)
        self.date = {
            "day": tomorrow.day,
            "year": tomorrow.year,
            "month":tomorrow.month,
            "day2": tomorrow.strftime("%d"),
            "month2": tomorrow.strftime("%m"),
            "monthname": tomorrow.strftime("%B"),
            "day+": dayAfterTomorrow.day,
            "year+": dayAfterTomorrow.year,
            "monthname+": dayAfterTomorrow.strftime("%B"),
            "day-": dayBeforeTomorrow.day,
            "year-": dayBeforeTomorrow.year,
            "monthname-": dayBeforeTomorrow.strftime("%B"),
            "day+7": weekAfterTomorrow.day,
            "year+7": weekAfterTomorrow.year,
            "monthname+7": weekAfterTomorrow.strftime("%B")
        }

    def getSummary(self):
        summary = "[[Wikipedia:Bots|Bot]]: Created daily sub"
        if self.page.namespace() == 14:
            summary += "category"
        else:
            summary += "page"
        return summary


    def submit(self, text, overwrite=False, revid=False):
        if not overwrite:
            if self.page.exists():
                return
        self.page.put(text, self.getSummary())
        if revid:
            return self.page.latestRevision()

    def run(self):
        for sub in self.subs:
            try:
                self.page = pywikibot.Page(site, self.subs[sub]["title"] % self.date)
                if isinstance(self.subs[sub]["text"], list):
                    if self.page.exists():
                        continue
                    revid = self.submit(self.subs[sub]["text"][0] % self.date, revid=True)
                    self.submit(
                        self.subs[sub]["text"][1] % dict(self.date.items() + [("revid", revid)]),
                        overwrite=True
                    )
                else:
                    self.submit(self.subs[sub]["text"] % self.date)
            except (Exception, pywikibot.Error), error:
                pywikibot.output(error)
                continue


def main():
    bot = SubCreatorBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
