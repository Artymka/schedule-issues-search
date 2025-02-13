import aiohttp
import asyncio
import icalendar
from functools import cmp_to_key

from utils.lesson import Lesson


async def get_search_json(search_param: str) -> dict:
    url = "https://schedule-of.mirea.ru/schedule/api/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"match": search_param, "limit": 1}) as response:
            res = await response.json()
            return res["data"][0]

async def get_calendar(search_res: dict):
    url = search_res["iCalLink"]
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            res = await response.read()
            return icalendar.Calendar.from_ical(res)


async def main():
    search_res = await get_search_json("ИКБО-70-24")
    cal = await get_calendar(search_res)

    for event in cal.walk("VEVENT"):
        print(event.get("SUMMARY"))
        print(event.get("RRULE"))
        # print(event)
        print(event.get("DTEND").dt - event.get("DTSTART").dt)
        # print(event.get("DTSTART").dt)

async def get_lessons_sequence(cal: icalendar.Calendar) -> list[Lesson]:
    # search_res = await get_search_json("ИКБО-70-24")
    # cal = await get_calendar(search_res)

    lessons_sequence = []
    for event in cal.walk("VEVENT"):
        # проверка на то, является ли event занятием
        if not event.get("RRULE"): continue

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

if __name__ == "__main__":
    asyncio.run(main())
