#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Published by Hazard-SJ (https://wikitech.wikimedia.org/wiki/User:Hazard-SJ)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/


import sys
import pywikibot
from datetime import datetime
from time import sleep


class SandBot(object):
    def __init__(self, dbName):
        self.loadConfig()
        self.dbName = dbName
        self.site = self.config[dbName]["site"]
        self.site.login()
        self.editsummary = pywikibot.i18n.twtranslate(self.site.language(), "clean_sandbox-cleaned")
        self.sandbots = self.config[dbName]["sandbots"]
        if self.config[dbName]["dotask"]:
            self.doTaskPage = pywikibot.Page(self.site, self.config[dbName]["dotask"])
        else:
            self.doTaskPage = None
        self.delay = 5

    def loadConfig(self):
        self.config = {
            "commonswiki": {
                "site": pywikibot.Site("commons", "commons"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "sandbots": ["Hazard-Bot", "O (bot)"],
                "sandboxes": {"Project:Sandbox": "general"},
                "groups": {"general": "{{Sandbox}}\n<!-- Please edit only below this line. -->"}
            },
            "enwiki": {
                "site": pywikibot.Site("en", "wikipedia"),
                "dotask": "User:Hazard-Bot/DoTask/SandBot",
                "sandbots": ["Addbot", "AvicBot2", "Hazard-Bot", "Lowercase sigmabot II"],
                "sandboxes": {
                    "Project:Sandbox": "general",
                    "Project talk:Sandbox": "general",
                    "Project:Tutorial/Citing sources/sandbox": "general",
                    "Project:Tutorial/Editing/sandbox": "general",
                    "Project:Tutorial/Formatting/sandbox": "general",
                    "Project:Tutorial/Keep in mind/sandbox": "general",
                    "Project:Tutorial/Wikipedia links/sandbox": "general",
                    "Project talk:Tutorial/Citing sources/sandbox": "general",
                    "Project talk:Tutorial/Editing/sandbox": "general",
                    "Project talk:Tutorial/Formatting/sandbox": "general",
                    "Project talk:Tutorial/Keep in mind/sandbox": "general",
                    "Project talk:Tutorial/Wikipedia links/sandbox": "general",
                    "Template:Template sandbox": "template",
                    "Template:X1": "template",
                    "Template:X2": "template",
                    "Template:X3": "template",
                    "Template:X4": "template",
                    "Template:X5": "template",
                    "Template:X6": "template",
                    "Template:X7": "template",
                    "Template:X8": "template",
                    "Template:X9": "template",
                    "Template:X10": "template",
                    "Template:X11": "template",
                    "Template:X12": "template",
                    "Template talk:X1": "general",
                    "Template talk:X2": "general",
                    "Template talk:X3": "general",
                    "Template talk:X4": "general",
                    "Template talk:X5": "general",
                    "Template talk:X6": "general",
                    "Template talk:X7": "general",
                    "Template talk:X9": "general",
                    "Template talk:X10": "general",
                    "Template talk:X11": "general",
                    "Template talk:X12": "general"
                },
                "groups": {
                    "general": u"{{subst:Sandbox reset}}",
                    "template": u"{{subst:Template sandbox reset}}"
                }
            },
            "mediawikiwiki": {
                "site": pywikibot.Site("mediawiki", "mediawiki"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "sandbots": ["Hazard-Bot"],
                "sandboxes": {"Project:Sandbox": "general"},
                "groups": {
                    "general": "{{Please leave this line alone and write below (this is the coloured heading)}}"
                }
            },
            "nlwiki": {
                "site": pywikibot.Site("nl", "wikipedia"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "sandbots": ["Hazard-Bot"],
                "sandboxes": {
                    "Project:Snelcursus/Probeer maar...": "tutorial",
                    "Project:Zandbak": "general"
                },
                "groups": {
                    "tutorial": "{{subst:/origineel}}",
                    "general": u"""\
<!-- Laat deze en de volgende regel a.u.b. altijd staan. -->{{Wikipedia:Zandbak/hoofding}}

== Wist je dat... ==

{{wistjedatjes}}

== Wikisyntax ==

[[hyperlink|interne link]]

[http://nl.wikipedia.org externe link]

*op
*som
*min
*gen

#ge
#num
#merd
##door
###num
####mer
#####en

<u>onderstreept</u>

<strike>doorgestreept</strike>

<big>groot</big>
<pre>pre-tekst</pre>

<code>code</code>

<tt>typewriter</tt>

<small>klein</small>

;tekst:serie letters en leestekens
;definitie:uitleg

Niet inspringen
:1 keer inspringen
::2 keer inspringen
:::*3 keer inspringen, met opsomming
::::*4 keer inspringen, met opsomming

== Sjabloon ==
<!-- Dit sjabloon is te bewerken op Wikipedia:Sjabloonzandbak, elke wijziging die je daar doorvoert, zal hieronder te zien zijn, zodat je kunt oefenen met sjablonen! -->

{{Wikipedia:Sjabloonzandbak}} 

== Tabel ==

{| class="wikitable"
|-
! seizoen
! club
! land
! competitie
! wed.
! goals
|-
| 1988/89 || [[RC Lens]] || {{FR}} || [[Championnat Ligue 1]] || 14 || 3
|-
| 1989/90 || [[Sporting Toulon Var]] || {{FR}} || [[Championnat Ligue 1]] || 3 || 0
|- 
| 1990/91 || [[Málaga CF]] || {{ES}} || [[Segunda División A]] || 5 || 0
|-
| 1991/92 || [[Málaga CF]] || {{ES}} || [[Segunda División B]] || 10 || 1
|-
| 1992/93 || [[Málaga CF]] || {{ES}} || [[Segunda División A]] || 7 || 0
|-
| 1993/94 || [[Maccabi Tel Aviv]] || {{IL}} || [[Ligat Ha'Al]] || 30 || 5
|-
|}

== Voorbeelden == 
[[Bestand:Flower Rex 1.jpg|thumb|right|Bloem]]

*******************
OZH = rechte van Euler: OH=<math>\sqrt[2]{9R^2-(a^2+b^2+c^2)}</math>

NZI = rechte van Nagel: NI=<math>\sqrt[2]{6r^2-12Rr+\frac{a^2+b^2+c^2}{2}}</math>

EZL = rechte van Lissajou: EL=<math>\sqrt[2]{9R^2+12r^2-6Rr-(a^2+b^2+c^2)}</math>
*******************
<math>F \cdot \Delta{s} = W</math>

<math> i \hbar {\partial\over\partial t} \psi(r,t)  = H \psi(r,t)</math>

==Terug naar de snelcursus==
Na het oefenen in de zandbak kunt u hier: [[Wikipedia:Snelcursus/Opmaken]] terug naar de snelcursus van deze Wikipedia.
""",
                }
            },
            "simplewiki": {
                "site": pywikibot.Site("simple", "wikipedia"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "sandbots": ["Hazard-Bot", "RileyBot"],
                "sandboxes": {
                    "Project:Sandbox": "general",
                    "Project:Introduction": "introduction",
                    "Project:Student tutorial": "tutorial"
                },
                "groups": {
                    "general": "{{subst:/Text}}",
                    "introduction": """{{/Content}}<!--Please leave this line alone-->
<!-- Feel free to change the text below this line. No profanity, please. -->
""",
                    "tutorial": """{{Wikipedia:Student tutorial/Nav bar}}
{{Please try your changes below this line}}"""
                }
            }
        }

    def checkDoTaskPage(self):
        if not self.doTaskPage:
            print "Note: No do-task page has been configured."
            return True
        try:
           text = self.doTaskPage.get(force = True)
        except pywikibot.IsRedirectPage:
            raise Warning("The 'do-task page' (%s) is a redirect." % self.doTaskPage.title(asLink = True))
        except pywikibot.NoPage:
            raise Warning("The 'do-task page' (%s) does not exist." % self.doTaskPage.title(asLink = True))
        else:
            if text.strip().lower() == "true":
                return True
            else:
                raise Exception("The task has been disabled from the 'do-task page' (%s)."
                    % self.doTaskPage.title(asLink = True)
                )

    def run(self):
        self.checkDoTaskPage()

        def cleanSandboxes(titles = self.config[self.dbName]["sandboxes"].keys()):
            self.recheck = list()
            for title in titles:
                sandbox = pywikibot.Page(self.site, title)
                try:
                    text = sandbox.get()
                    group = self.config[self.dbName]["sandboxes"][title]
                    groupText = self.config[self.dbName]["groups"][group]
                    if text.strip() == groupText.strip():
                        print "Skipping [[%s]]: Sandbox is clean" % title
                        continue
                    elif sandbox.userName() in self.sandbots:
                        print "Skipping [[%s]]: Sandbot version" % title
                        continue
                    else:
                        diff = datetime.utcnow() - sandbox.editTime()
                        if (diff.seconds/60) >= self.delay:
                            try:
                                sandbox.put(groupText, comment=self.editsummary)
                            except pywikibot.EditConflict:
                                self.recheck.append(title)
                                print "Delaying [[%s]]: Edit conflict encountered" % title
                        else:
                            self.recheck.append(title)
                            print "Delaying [[%s]]: Sandbox may still be in use" % title
                except pywikibot.NoPage:
                    print "Skipping [[%s]]: Non-existent sandbox" % title

        cleanSandboxes()
        rechecks = 0
        while (len(self.recheck) > 0) and (rechecks > 2):
            rechecks += 1
            pause = self.delay * 60
            print "Pausing %i seconds to recheck %i sandboxes %s" % (pause, len(self.recheck), tuple(self.recheck))
            sleep(pause)
            cleanSandboxes(self.recheck)

class SandHeaderBot(object):
    def __init__(self, dbName):
        self.dbName = dbName
        self.config = {
            "enwiki": {}
        }
            


def main():
    sandBotSites = ["commonswiki", "enwiki", "mediawikiwiki", "nlwiki", "simplewiki"]
    sandBotHeaderSites = list()  # The class has not yet been completed  # ["enwiki"]
    dbName = None
    header = False
    if len(sys.argv) > 1:
        dbName = sys.argv[1]
        if "--header" in sys.argv:
            header = True
    else:
        dbName = raw_input("Enter the database name (without '_p'): ")
        if dbName in sandBotHeaderSites:
            header = input("Only insert header [True/False]: ")
    if not dbName in sandBotSites:
        raise Exception("%s is not configured as a sandbot site.")
    if header:
        if not dbName in sandBotHeaderSites:
            raise Exception("%s is not configured as a sandbot header site.")
        else:
            bot = SandHeaderBot(dbName)
    else:
        bot = SandBot(dbName)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
