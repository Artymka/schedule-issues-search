import aiohttp
import asyncio
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import schedule


from db.db import DB
from update_data import update_issues, update_targets

app = FastAPI()

@app.get("/api/search")
async def get_schedule_issues(search_param: str | None):
    db = await DB(min_size=1, max_size=10,
                  host="127.0.0.1",
                  database="schedule_issues",
                  port=5432,
                  user="postgres",
                  password="root")

    if not search_param:
        issues = await db.get_all_issues()
        return JSONResponse(content=jsonable_encoder(issues))

    issues = await db.get_filtered_issues(search_param)
    return JSONResponse(content=issues)


async def main():
    session = aiohttp.ClientSession()
    db = await DB(min_size=1, max_size=10,
                  host="127.0.0.1",
                  database="schedule_issues",
                  port=5432,
                  user="postgres",
                  password="root")

    schedule.every().day.at("10:00").do(update_issues, session, db)
    schedule.every().week.do(update_targets, session, db)

if __name__ == "__main__":
    asyncio.run(main())