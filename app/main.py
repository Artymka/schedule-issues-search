import aiohttp
from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


from db.db import DB


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

    # search_json = await get_search_json(search_param)
    # cal = await get_calendar(search_json)
    # lessons_sequence = await get_lessons_sequence(cal)
    #
    # issues = search_window_issues(lessons_sequence)
    # json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
    # return Response(content=json_str, media_type="application/json")

# @app.get("/window/{search_param}")
# async def get_window_issues(search_param: str):
#     search_json = await get_search_json(search_param)
#     cal = await get_calendar(search_json)
#     lessons_sequence = await get_lessons_sequence(cal)
#
#     issues = search_window_issues(lessons_sequence)
#     json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
#     return Response(content=json_str, media_type="application/json")
#
# @app.get("/jogging/{search_param}")
# async def get_jogging_issues(search_param: str):
#     search_json = await get_search_json(search_param)
#     cal = await get_calendar(search_json)
#     lessons_sequence = await get_lessons_sequence(cal)
#
#     issues = search_jogging_issues(lessons_sequence)
#     json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
#     return Response(content=json_str, media_type="application/json")
#
# @app.get("/insomnia/{search_param}")
# async def get_insomnia_issues(search_param: str):
#     search_json = await get_search_json(search_param)
#     cal = await get_calendar(search_json)
#     lessons_sequence = await get_lessons_sequence(cal)
#
#     issues = search_insomnia_issues(lessons_sequence)
#     json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
#     return Response(content=json_str, media_type="application/json")
#
# @app.get("/all/{search_param}")
# async def get_all_issues(search_param: str):
#     search_json = await get_search_json(search_param)
#     cal = await get_calendar(search_json)
#     lessons_sequence = await get_lessons_sequence(cal)
#
#     windows_issues = search_window_issues(lessons_sequence)
#     jogging_issues = search_jogging_issues(lessons_sequence)
#     insomnia_issues = search_insomnia_issues(lessons_sequence)
#     issues = windows_issues + jogging_issues + insomnia_issues
#
#     json_str = json.dumps([issue.formatted() for issue in issues], ensure_ascii=False)
#     return Response(content=json_str, media_type="application/json")