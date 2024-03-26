from datetime import datetime
from re import findall
import sys
from time import sleep

import pywikibot


class SandBot(object):
    def __init__(self, db_name):
        self.load_config()
        self.db_name = db_name
        self.site = self.config[db_name]["site"]
        self.site.login()
        # TODO: Figure out why this isn't workng on Toolforge k8s, or remove it.
        # self.edit_summary = pywikibot.i18n.twtranslate(self.site, "clean_sandbox-cleaned")
        self.edit_summary = self.config[db_name]["edit_summary"]
        self.sandbots = self.config[db_name]["sandbots"]
        if self.config[db_name]["dotask"]:
            self.do_task_page = pywikibot.Page(self.site, self.config[db_name]["dotask"])
        else:
            self.do_task_page = None
        self.delay = 10  # number of minutes sandbox should have not been used for before cleaning

    def load_config(self):
        self.config = {
            "commonswiki": {
                "site": pywikibot.Site("commons", "commons"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "Bot: Automatically cleaned",
                "sandbots": ["Hazard-Bot", "O (bot)"],
                "sandboxes": {"Project:Sandbox": "general"},
                "groups": {"general": "{{Sandbox}}\n<!-- Please edit only below this line. -->"},
            },
            "enwiki": {
                "site": pywikibot.Site("en", "wikipedia"),
                "dotask": "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "Bot: Automatically cleaned",
                "sandbots": ["Addbot", "AvicBot2", "Cyberbot I", "Hazard-Bot", "Lowercase sigmabot II"],
                "sandboxes": {
                    "Draft:Sandbox": "general",
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
                    "Template talk:X12": "general",
                    "User:Sandbox": "general",
                    "User talk:Sandbox": "general"
                },
                "groups": {
                    "general": "{{subst:Sandbox reset}}",
                    "template": "{{subst:Template sandbox reset}}"
                },
            },
            "mediawikiwiki": {
                "site": pywikibot.Site("mediawiki", "mediawiki"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "Bot: Automatically cleaned",
                "sandbots": ["Hazard-Bot"],
                "sandboxes": {
                    "Project:Sandbox": "general",
                    "Project:VisualEditor testing/Test": "visualeditor"
                },
                "groups": {
                    "general": "{{Please leave this line alone and write below (this is the coloured heading)}}",
                    "visualeditor": "{{subst:Project:VisualEditor testing/Test/Text}}"
                },
            },
            "nlwiki": {
                "site": pywikibot.Site("nl", "wikipedia"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "Robot: automatisch opgeruimd",
                "sandbots": ["Hazard-Bot"],
                "sandboxes": {
                    "Project:Snelcursus/Probeer maar...": "tutorial",
                    "Project:Zandbak": "general"
                },
                "groups": {
                    "tutorial": "{{subst:/origineel}}",
                    "general": "{{subst:/origineel}}",
                },
            },
            "simplewiki": {
                "site": pywikibot.Site("simple", "wikipedia"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "Bot: Automatically cleaned",
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
                },
            },
            "sqwiki": {
                "site": pywikibot.Site("sq", "wikipedia"),
                "dotask": None,  # "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "Roboti: Pastrim automatik",
                "sandbots": ["Hazard-Bot"],
                "sandboxes": {
                    "Project:Livadhi": "general",
                },
                "groups": {
                    "general": """{{Livadhi}}<!--
*      Mirë se erdhët në Livadhin e Wikipedia-s!   *
*          Ju lutemi, mos e fshini këtë pjesë.    *
*        Kjo faqe pastrohet rregullisht.          *
*   Provoni aftësitë tuaja të redaktimit poshtë.  *
■■■■ ■■■■■ ■■■■■■■■■■■■■■■■■■■■■■■ ■■■■ ■■■■■■■■ ■■■■■ ■■■■■-->
""",
                },
            },
        }

    def check_do_task_page(self):
        if not self.do_task_page:
            print("Note: No do-task page has been configured.")
            return True
        try:
            text = self.do_task_page.get(force=True)
        except pywikibot.IsRedirectPage:
            raise Warning("The 'do-task page' (%s) is a redirect." % self.do_task_page.title(asLink=True))
        except pywikibot.NoPage:
            raise Warning("The 'do-task page' (%s) does not exist." % self.do_task_page.title(asLink=True))
        else:
            if text.strip().lower() == "true":
                return True
            else:
                raise Exception("The task has been disabled from the 'do-task page' (%s)." %
                                self.do_task_page.title(asLink=True)
                                )

    def run(self):
        self.check_do_task_page()

        def clean_sandboxes(titles=self.config[self.db_name]["sandboxes"].keys()):
            self.recheck = list()
            for title in titles:
                sandbox = pywikibot.Page(self.site, title)
                try:
                    text = sandbox.get()
                    group = self.config[self.db_name]["sandboxes"][title]
                    group_text = self.config[self.db_name]["groups"][group]
                    if text.strip() == group_text.strip():
                        print("Skipping [[%s]]: Sandbox is clean" % title)
                        continue
                    elif sandbox.userName() in self.sandbots:
                        print("Skipping [[%s]]: Sandbot version" % title)
                        continue
                    else:
                        diff = datetime.utcnow() - sandbox.editTime()
                        if (diff.seconds/60) >= self.delay:
                            try:
                                sandbox.put(group_text, self.edit_summary)
                            except pywikibot.EditConflict:
                                self.recheck.append(title)
                                print("Delaying [[%s]]: Edit conflict encountered" % title)
                        else:
                            self.recheck.append(title)
                            print("Delaying [[%s]]: Sandbox may still be in use" % title)
                except pywikibot.NoPage:
                    print("Skipping [[%s]]: Non-existent sandbox" % title)

        clean_sandboxes()
        rechecks = 0
        while (len(self.recheck) > 0) and (rechecks > 2):
            rechecks += 1
            pause = 3 * 60
            print("Pausing %i seconds to recheck %i sandboxes %s" % (pause, len(self.recheck), tuple(self.recheck)))
            sleep(pause)
            clean_sandboxes(self.recheck)


class SandHeaderBot(SandBot):
    def __init__(self, db_name):
        self.db_name = db_name
        self.config = {
            "enwiki": {
                "site": pywikibot.Site("en", "wikipedia"),
                "dotask": "User:Hazard-Bot/DoTask/SandBot",
                "edit_summary": "[[Wikipedia:Bots|Bot]]: Reinserting sandbox header",
                "template": "Template:Sandbox heading",
                "sandboxes": {"Project:Sandbox": "general"},
                "groups": {"general": "{{subst:Sandbox reset}}"}
            }
        }
        self.site = self.config[db_name]["site"]
        self.site.login()
        self.do_task_page = pywikibot.Page(self.site, self.config[db_name]["dotask"])
        self.edit_summary = self.config[db_name]["edit_summary"]

    def _get_titles(self, template):
        """Gets a list of the lowercase titles of a template and its redirects"""
        titles = [template.title(with_ns=False).lower()]
        for reference in template.getReferences(with_template_inclusion=False, filter_redirects=True):
            titles.append(reference.title(with_ns=False).lower())
        return list(set(titles))

    def run(self):
        self.check_do_task_page()
        for title in self.config[self.db_name]["sandboxes"].keys():
            sandbox = pywikibot.Page(self.site, title)
            text = sandbox.get(force=True)
            found = False
            for template in self._get_titles(pywikibot.Page(self.site, self.config[self.db_name]["template"])):
                if findall("\{\{\s*%s\s*\}\}" % (template.replace("(", "\(").replace(")", "\)")), text.lower()):
                    found = True
                    break
            if not found:
                group = self.config[self.db_name]["sandboxes"][title]
                group_text = self.config[self.db_name]["groups"][group]
                try:
                    sandbox.put("%s\n\n%s" % (group_text, text), self.edit_summary)
                except pywikibot.Error:
                    continue


def main():
    sandbot_sites = ["commonswiki", "enwiki", "mediawikiwiki", "nlwiki", "simplewiki"]
    sandbot_header_sites = ["enwiki"]
    header = False
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
        if "--header" in sys.argv:
            header = True
    else:
        # Whether Python 2 or 3, we want the string
        def prompt(text):
            try:
                value = raw_input(text)
            except NameError:
                value = input(text)
            finally:
                return value

        db_name = prompt("Enter the database name (without '_p'): ")
        if db_name in sandbot_header_sites:
            header = prompt("Only insert header [True/False]: ")
            if header.lower().startswith("t"):
                header = True
            else:
                header = False
    if db_name not in sandbot_sites:
        raise Exception("%s is not configured as a sandbot site.")
    if header:
        if db_name not in sandbot_header_sites:
            raise Exception("%s is not configured as a sandbot header site.")
        else:
            bot = SandHeaderBot(db_name)
    else:
        bot = SandBot(db_name)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
