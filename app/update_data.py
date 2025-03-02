import aiohttp

from db.db import DB
from schedule import save_key_targets, \
                     get_all_pages, \
                     get_calendar, \
                     get_lessons_sequence
from search_issues import search_all_issues


async def update_targets(session: aiohttp.ClientSession, db: DB):
    pages_data = await get_all_pages(session)
    await save_key_targets(pages_data, db)


async def update_issues(session: aiohttp.ClientSession, db: DB):
    targets = await db.get_all_targets()
    issues = []

    for target in targets:
        cal = await get_calendar(session, target["ical_link"])
        lessons_sequence = await get_lessons_sequence(cal)
        issues += search_all_issues(lessons_sequence)

    await db.update_issues([issue.formatted() for issue in issues])