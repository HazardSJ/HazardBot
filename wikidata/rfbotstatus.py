#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import mwparserfromhell
import pywikibot


pywikibot.config.family = "wikidata"
pywikibot.config.mylang = "wikidata"

site = pywikibot.Site()
site.login()

rfbotPage = pywikibot.Page(site, "Wikidata:Requests for permissions/Bot")
statusPage = pywikibot.Page(site, rfbotPage.title() + "/Status")

rfbotCode = mwparserfromhell.parse(rfbotPage.get())

prefix = rfbotPage.title() + "/"
requests = list()

for this in rfbotCode.ifilter_templates():
    if this.name.lower().strip().startswith(prefix.lower()):
        if not ("header" in this.name.lower() or "status" in this.name.lower()):
            requests.append(this.name.strip().split("/")[-1])

template = """\
{| border="1" class="wikitable sortable plainlinks"
!Bot Name !! Request created !! Last editor !! Last edited
%s
|}
"""
data = list()
rows = list()

for request in requests:
    page = pywikibot.Page(site, prefix + request)
    if not page.exists():
        continue
    history = page.getVersionHistory()
    created = history[-1][1]
    edit = history[0][0]
    edited = history[0][1]
    editor = history[0][2]
    row = """\
|-
| [[%s|%s]] || %s || %s || %s\
""" % (
    page.title(),
    request,
    str(created)[:10] + ", " + str(created)[11:19],
    editor,
    "[{{SERVER}}/wiki/?diff=" + str(edit) + " " + str(edited)[:10] + ", " + str(edited)[11:19] +"]"
)
    rows.append(row)
   
status = template % "\n".join(rows)
statusPage.put(status, comment="[[Wikidata:Bots|Bot]]: Updating RFBOT status")
pywikibot.stopme()
