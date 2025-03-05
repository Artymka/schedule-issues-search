import aiohttp

from db.db import DB
from schedule_data import save_key_targets, \
                     get_all_pages, \
                     get_calendar, \
                     get_lessons_sequence
from search_issues import search_all_issues


async def update_targets(db: DB):
    print("update targets")
    async with aiohttp.ClientSession() as session:
        pages_data = await get_all_pages(session)
        await save_key_targets(pages_data, db)


async def update_issues(db: DB):
    print("update issues")
    targets = await db.get_all_targets()
    issues = []

    async with aiohttp.ClientSession() as session:
        for target in targets:
            cal = await get_calendar(session, target["ical_link"])
            lessons_sequence = await get_lessons_sequence(cal)
            issues += search_all_issues(lessons_sequence, target["id"])

    await db.update_issues([issue.formatted() for issue in issues])