# -*- coding: utf-8 -*-
#
# This work by Hazard-SJ ( https://github.com/HazardSJ ) is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License ( http://creativecommons.org/licenses/by-sa/4.0/ ).


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
    def __init__(self, requester=None):
        self.requester = requester
        self.subDirName = "flickrUKFCO"  # determines the sub-directory it uses
        self.uploadByURL = "upload_by_url" in site.getuserinfo()["rights"]
        self.baseURL = "https://secure.flickr.com/photos/foreignoffice/"
        self.imageDescription = """\
== {{int:filedesc}} ==
{{Information
|description={{en|1=%(description)s}}
|date=%(date)s
|source=%(source)s
|author={{en|1=%(owner)s}}
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
                except KeyboardInterrupt:
                    raise pywikibot.Error("Keyboard interrupted")
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
        imagePage = pywikibot.ImagePage(site, name)
        imagePage.text = self.imageDescription % {
            "date": fileDate,
            "description": fileDescription,
            "owner": fileOwner,
            "source": pageURL
        }
        if self.uploadByURL:
            site.upload(imagePage, source_url=fileURL, comment=self.summary)
        else:
            path = os.path.abspath(
                os.path.join(
                    self.subDirName,
                    name
                )
            )
            urllib.urlretrieve(fileURL, path)
            site.upload(imagePage, source_filename=path, comment=self.summary)
            os.remove(path)

    def ensureSubDir(self):
        directory = os.path.abspath(self.subDirName)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def run(self):
        if not self.requester:
            raise pywikibot.Error("No requester is set")
        else:
            self.summary = "[[Commons:Bots|Bot]]: Uploading files from Flickr per request by [[User:%s|%s]]" \
                % (self.requester, self.requester)
        if not self.uploadByURL:
            self.ensureSubDir()
        self.parsePages()

def main():
    requester = "Russavia"
    bot = FlickrUploadBot(requester = requester)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
