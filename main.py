import aiohttp
import asyncio
from fastapi import FastAPI, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import schedule
from typing import Annotated
import uvicorn

from db.db import DB
from update_data import update_issues, update_targets


async def get_db() -> DB:
    return await DB(min_size=1, max_size=10,
                  host="127.0.0.1",
                  database="schedule_issues",
                  port=5432,
                  user="postgres",
                  password="root")

async def start_scheduling():
    session = aiohttp.ClientSession()
    db = await get_db()

    await update_targets(db)
    await update_issues(db)

    schedule.every().day.at("10:00").do(update_issues, db)
    schedule.every().week.do(update_targets, db)


app = FastAPI()

@app.get("/api/search")
async def get_schedule_issues(query: Annotated[str | None, Query(max_length=100)] = None,
                              db: Annotated[DB, Depends(get_db)] = None):
    if not query:
        issues = await db.get_all_issues()
        return JSONResponse(content=jsonable_encoder(issues))

    issues = await db.get_filtered_issues(query)
    return JSONResponse(content=issues)

async def main():
    await start_scheduling()
    uvicorn.run(app)

if __name__ == "__main__":
    asyncio.run(main())