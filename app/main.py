from fastapi import FastAPI, Response
import json

from .search_issues import search_insomnia_issues, \
                          search_jogging_issues, \
                          search_window_issues
from utils.utils import get_search_json, \
                        get_calendar, \
                        get_lessons_sequence
from utils.schedules_issue import SchedulesIssue


app = FastAPI()

@app.get("/window/{search_param}")
async def get_window_issues(search_param: str):
    search_json = await get_search_json(search_param)
    cal = await get_calendar(search_json)
    lessons_sequence = await get_lessons_sequence(cal)

    issues = search_window_issues(lessons_sequence)
    json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
    return Response(content=json_str, media_type="application/json")

@app.get("/jogging/{search_param}")
async def get_jogging_issues(search_param: str):
    search_json = await get_search_json(search_param)
    cal = await get_calendar(search_json)
    lessons_sequence = await get_lessons_sequence(cal)

    issues = search_jogging_issues(lessons_sequence)
    json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
    return Response(content=json_str, media_type="application/json")

@app.get("/insomnia/{search_param}")
async def get_insomnia_issues(search_param: str):
    search_json = await get_search_json(search_param)
    cal = await get_calendar(search_json)
    lessons_sequence = await get_lessons_sequence(cal)

    issues = search_insomnia_issues(lessons_sequence)
    json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
    return Response(content=json_str, media_type="application/json")

@app.get("/all/{search_param}")
async def get_all_issues(search_param: str):
    search_json = await get_search_json(search_param)
    cal = await get_calendar(search_json)
    lessons_sequence = await get_lessons_sequence(cal)

    windows_issues = search_window_issues(lessons_sequence)
    jogging_issues = search_jogging_issues(lessons_sequence)
    insomnia_issues = search_insomnia_issues(lessons_sequence)
    issues = windows_issues + jogging_issues + insomnia_issues

    json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
    return Response(content=json_str, media_type="application/json")