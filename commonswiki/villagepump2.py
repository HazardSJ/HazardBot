from datetime import datetime

import mwparserfromhell
import pywikibot


pywikibot.config.family = "commons"
pywikibot.config.mylang = "commons"

site = pywikibot.Site()
site.login()

page = pywikibot.Page(site, "Commons:Village pump")


def check_do_task_page():
    do_task_page = pywikibot.Page(site, "User:Hazard-Bot/DoTask/Villagepump")
    if not do_task_page:
        print("Note: No do-task page has been configured.")
        return
    try:
       text = do_task_page.get(force=True)
    except pywikibot.IsRedirectPage:
        raise Exception(
            "The 'do-task page' (%s) is a redirect."
            % do_task_page.title(asLink=True)
        )
    except pywikibot.NoPage:
        raise Exception(
            "The 'do-task page' (%s) does not exist."
            % do_task_page.title(asLink=True)
        )
    if text.strip().lower() != "true":
        raise Exception(
            "The task has been disabled from the 'do-task page' (%s)."
            % do_task_page.title(asLink=True)
        )


def _is_todays_section(heading, todays_date):
    return heading.title.strip() == todays_date


def remove_empty_sections(text, todays_date):
    removed_count = 0
    for section in text.get_sections(levels=[1]):
        heading = section.nodes[0]
        body = section.nodes[1:]
        is_empty_body = not any(n.strip() for n in body)
        if is_empty_body and not _is_todays_section(heading, todays_date):
            text.remove(section)
            removed_count += 1
    print("Removed %d empty sections" % removed_count)
    return removed_count


def add_todays_section(text, todays_date):
    for heading in text.ifilter_headings(matches=lambda h: h.level == 1):
        if _is_todays_section(heading, todays_date):
            print("Today's section was already created")
            return False
    text.append("\n\n= %s =" % todays_date)
    print("Added today's section")
    return True


def main():
    text = page.get()
    text = mwparserfromhell.parse(text)

    todays_date = datetime.strftime(datetime.utcnow(), "%B %d")

    summary = []

    removed_count = remove_empty_sections(text, todays_date)
    if removed_count:
        summary.append(
            "removed an empty section"
            if removed_count == 1 else
            "removed %d empty sections" % removed_count
        )

    if add_todays_section(text, todays_date):
        summary.append("added daily section heading for %s" % todays_date)

    page.text = text
    page.save(
        summary="[[Commons:Bots|Bot]]: %s" % "; ".join(summary),
    )


if __name__ == "__main__":
    try:
        check_do_task_page()
        main()
    finally:
        pywikibot.stopme()
