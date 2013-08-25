#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import json
import os
import re
import urllib
import urllib2

import pywikibot


pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()

class FlickrUploadBot(object):
    def __init__(self):
        self.subDirName = "flickrUKFCO"  # determines the sub-directory it uses
        self.baseURL = "https://secure.flickr.com/photos/foreignoffice/"
        self.imageDescription = """\
== {{int:filedesc}} ==
{{Information
|description={{en|1=%(description)s}}
|date=%(date)s
|source=%(source)s
|author=%(owner)s
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
            for line in urllib2.urlopen(pageURL):
                pageText += line
            photoIDs = re.finditer(
                '<span class="photo_container pc_ju">.*?<a data-track="photo-click"  href="/photos/foreignoffice/(\d+)/" title="\D+".*?</span>',
                pageText,
                re.DOTALL
            )
            for photoID in photoIDs:
                try:
                    self.parsePhoto(photoID.group(1))
                except:
                    continue

    def parsePhoto(self, photoID):
        pageURL = self.baseURL + photoID
        pageText = ""
        for line in urllib2.urlopen(pageURL):
            pageText += line
        fileData = json.loads(
            re.findall("Y\.photo\.init\((.*?)\);", pageText, re.S)[0]
        )
        fileTitle = fileData["title"]
        fileDescription = fileData["description"]
        fileDate = fileData["date_taken"]
        fileOwner = fileData["ownername"]
        fileURL = fileData["sizes"]["o"]["url"]
        fileExtension = fileURL.split(".")[-1]
        name = "%s (%s).%s" % (fileTitle, photoID, fileExtension)
        path = os.path.abspath(
            os.path.join(
                self.subDirName,
                name
            )
        )
        urllib.urlretrieve(fileURL, path)
        imagePage = pywikibot.ImagePage(site, name)
        imagePage.text = self.imageDescription % {
            "date": fileDate,
            "description": fileDescription,
            "owner": fileOwner,
            "source": pageURL
        }
        site.upload(imagePage, source_filename=path)
        os.remove(path)

    def ensureSubDir(self):
        directory = os.path.abspath(self.subDirName)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def run(self):
        self.ensureSubDir()
        self.parsePages()

def main():
    bot = FlickrUploadBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
