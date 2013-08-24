#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import os
import re
import urllib
import urllib2

import pywikibot
from bs4 import BeautifulSoup
import dateutil.parser as dateparser  # http://labix.org/python-dateutil


pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()

class FlickrUploadBot(object):
    def __init__(self):
        self.baseURL = "https://secure.flickr.com/photos/foreignoffice/"
        self.imageDescription = """\
== {{int:filedesc}} ==
{{Information
|description={{en|1=%(description)s}}
|date=%(date)s
|source=%(source)s
|author=Foreign and Commonwealth Office
|permission=
|other_versions=
|other_fields=
}}

== {{int:license-header}} ==
{{FCO}}

[[Category:Files from Foreign and Commonwealth Office Flickr stream (to check)]]
"""

    def parsePages(self):
        for pageNumber in range(1, 40):
            pageURL = self.baseURL + "page" + str(pageNumber) + "/"
            pageText = ""
            # pageURL = urllib2.Request(pageURL, headers={"User-Agent": "Python Wikimedia Commons Uploader"})  ##
            for line in urllib2.urlopen(pageURL):
                pageText += line
            photoIDs = re.finditer(
                '<span class="photo_container pc_ju">.*?<a data-track="photo-click"  href="/photos/foreignoffice/(\d+)/" title="\D+".*?</span>',
                pageText,
                re.DOTALL
            )
            for photoID in photoIDs:
                self.parsePhoto(photoID.group(1))

    def parsePhoto(self, photoID):
        pageURL = self.baseURL + photoID  # + "/in/photostream/"
        pageText = ""
        for line in urllib2.urlopen(pageURL):
            pageText += line
        fileTitle = re.findall('<meta name="title" content="(.*?)">', pageText, re.S)[0]
        fileDescription = BeautifulSoup(
            re.findall('<meta name="description" content="(.*?)">', pageText, re.S)[0]
        ).get_text()
        try:
            fileDate = re.findall(
                'Taken on <a href="/photos/foreignoffice/archives/date-taken/(.*?)/" title="Uploaded .*? " class="ywa-track" data-ywa-name="Date, Taken on">.*?</a>',
                pageText,
                re.S
            )[0].replace("/", "-")
        except:
            fileDate = ""
        if not fileDate:
            try:
                dateParse = dateparser.parse(fileDescription)
                fileDate = "%s-%s-%s" % (
                    dateParse.year,
                    dateParse.month if dateParse.month > 9 else "0%s" % dateParse.month,
                    dateParse.day if dateParse.day > 9 else "0%s" % dateParse.day
                )
            except:
                fileDate = ""
        fileURL = re.findall('<script>.*?var photo = \{.*?baseURL: (.*?),.*?\}.*?</script>', pageText, re.S)[0][1:-1]
        name = "%s (%s)" % (fileTitle, photoID)
        path = os.path.abspath(
            os.path.join(
                "flickrUKFCO",
                name
            )
        )
        urllib.urlretrieve(pageURL, path)
        imagePage = pywikibot.ImagePage(site, name)
        imagePage.text = self.imageDescription % {
            description: fileDescription,
            date: fileDate,
            source: pageURL
        }
        site.upload(imagePage, source_filename=path)
        os.remove(path)

    def run(self):
        return self.parsePages()

def main():
    bot = FlickrUploadBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
