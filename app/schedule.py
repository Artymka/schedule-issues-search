import aiohttp
import asyncio
import icalendar
from functools import cmp_to_key

# from .lesson import Lesson
from utils.lesson import Lesson
from utils.target import Target
from db.db import DB


async def get_search_json(search_param: str) -> dict:
    url = "https://schedule-of.mirea.ru/schedule/api/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"match": search_param, "limit": 1}) as response:
            res = await response.json()
            return res["data"][0]


async def get_all_pages(session: aiohttp.ClientSession,
                        url: str = "https://schedule-of.mirea.ru/schedule/api/search") -> list[dict]:
    page_token = ""
    pages_data = []
    fl = True

    async with session:
        while fl:
            async with session.get(url, params={"pagetoken": page_token}) as response:
                res = await response.json()
                page_token = res["nextPageToken"]
                pages_data += res["data"]

                if not page_token: fl = False

    return pages_data


async def save_key_targets(pages_data: list[dict], db: DB):
    targets_data = []

    def cut_title(title: str) -> str:
        return title.lower().replace(" ", "").replace("-", "")

    for target in pages_data:
        if target["scheduleTarget"] not in (1, 2): continue
        targets_data.append({
            "id": target["id"],
            "title": target["fullTitle"],
            "short_title": cut_title(target["fullTitle"]),
            "ical_link": target["iCalLink"],
        })

    await db.update_targets(targets_data)


async def get_calendar(session: aiohttp.ClientSession, url: str) -> icalendar.Calendar:
    async with session.get(url) as response:
        res = await response.read()
        return icalendar.Calendar.from_ical(res)


async def get_lessons_sequence(cal: icalendar.Calendar) -> list[Lesson]:
    lessons_sequence = []

    for event in cal.walk("VEVENT"):
        # проверка на то, является ли event занятием
        if not event.get("RRULE"): continue
        # проверка на то, является ли пара дистанционной
        if event.get("LOCATION") == "Дистанционно (СДО)": continue

        lessons_sequence.append(Lesson(
            event.get("SUMMARY"),
            event.get("LOCATION"),
            event.get("DTSTART").dt,
            event.get("DTEND").dt
        ))

    def compare(lesson1: Lesson, lesson2: Lesson):
        return int((lesson1.start_time - lesson2.start_time).total_seconds())

    lessons_sequence.sort(key=cmp_to_key(compare))
    return lessons_sequence







async def main():
    # search_res = await get_search_json("ИКБО-70-24")
    # cal = await get_calendar(search_res)
    # for event in cal.walk("VEVENT"):
    #     print(event)
    #     print(event.get("SUMMARY"))
    #     print(event.get("DESCRIPTION"))
    # lessons = await get_lessons_sequence(cal)
    # for lesson in lessons:
    #     print(lesson.room)

    # page_token = ""
    # for i in range(100):
    #     api_json = await get_api_json(page_token)
    #     page_token = api_json["nextPageToken"]
    #     if not page_token: break
    #     for record in api_json["data"]:
    #         print(record["scheduleTarget"], record["targetTitle"])

    db = await DB(min_size=1, max_size=10,
                  host="127.0.0.1",
                  database="schedule_issues",
                  port=5432,
                  user="postgres",
                  password="root")

    async with aiohttp.ClientSession() as session:
        await save_key_targets(await get_all_pages(session), db)


if __name__ == "__main__":
    asyncio.run(main())
