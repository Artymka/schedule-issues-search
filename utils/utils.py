import aiohttp
import asyncio
import icalendar


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

if __name__ == "__main__":
    asyncio.run(main())
