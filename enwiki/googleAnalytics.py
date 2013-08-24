#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import MySQLdb
import pywikibot


pywikibot.config.family = "wikipedia"
pywikibot.config.mylang = "en"

site = pywikibot.Site()
site.login()
page = pywikibot.Page(site, "User:Hazard-Bot/Google Analytics report")

connection = MySQLdb.connect(
    host = "enwiki.labsdb",
    db = "enwiki_p",
    read_default_file = "~/replica.my.cnf"
)
cursor = connection.cursor()
query = '''\
SELECT page_title, el_to
FROM externallinks
JOIN page
ON page_id = el_from
WHERE el_to LIKE "%&utm_%=%"
AND page_namespace = 0
LIMIT 500;
'''
cursor.execute(query)

text = "Pages containing links tracked by Google Analytics:\n\n"
for title, link in cursor.fetchall():
    text += "# [[%s]]: %s\n" % (title, link)

pywikibot.data.api.Request(
    action="edit",
    title=page.title(),
    text=text,
    token=site.token(page, "edit"),
    summary="Robot: generated list of pages with links tracked by Google Analytics",
    bot=1
).submit()
# page.put(text, comment="Robot: generated list of pages with links tracked by Google Analytics")