import aiohttp
import asyncio
import icalendar
from functools import cmp_to_key

# from .lesson import Lesson
from lesson import Lesson

async def get_search_json(search_param: str) -> dict:
    url = "https://schedule-of.mirea.ru/schedule/api/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"match": search_param, "limit": 1}) as response:
            res = await response.json()
            return res["data"][0]


async def get_all_pages():
    url = "https://schedule-of.mirea.ru/schedule/api/search"
    page_token = ""
    pages_data = []
    fl = True

    async with aiohttp.ClientSession() as session:
        while fl:
            async with session.get(url, params={"pagetoken": page_token}) as response:
                res = await response.json()
                page_token = res["nextPageToken"]
                pages_data += res["data"]

                if not page_token: fl = False

    return pages_data

async def get_targets_from_json(pages_data):
    targets = []
    for target in pages_data:
        if target["scheduleTarget"] not in (1, 2): continue





async def get_api_json(page_token: str = "") -> dict:
    url = "https://schedule-of.mirea.ru/schedule/api/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"pagetoken": page_token}) as response:
            res = await response.json()
            return res

async def get_calendar(search_res: dict):
    url = search_res["iCalLink"]
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            res = await response.read()
            return icalendar.Calendar.from_ical(res)

async def get_lessons_sequence(cal: icalendar.Calendar) -> list[Lesson]:
    # search_res = await get_search_json("ИКБО-70-24")
    # cal = await get_calendar(search_res)

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
        # res = int((lesson1.start_time - lesson2.start_time).total_seconds())
        # print("***", res)
        # print(lesson1.name, lesson1.start_time)
        # print(lesson2.name, lesson2.start_time)
        return int((lesson1.start_time - lesson2.start_time).total_seconds())

    lessons_sequence.sort(key=cmp_to_key(compare))
    return lessons_sequence


async def main():
    search_res = await get_search_json("ИКБО-70-24")
    cal = await get_calendar(search_res)
    for event in cal.walk("VEVENT"):
        print(event)
        print(event.get("SUMMARY"))
        print(event.get("DESCRIPTION"))
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


if __name__ == "__main__":
    asyncio.run(main())
