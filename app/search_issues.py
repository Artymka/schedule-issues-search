import asyncio
import icalendar
from datetime import datetime, time, timedelta
from functools import cmp_to_key

from utils.utils import get_search_json, get_calendar
from utils.lesson import Lesson
from utils.schedules_issue import SchedulesIssue

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

def get_window_issues(lessons_sequence: list[Lesson]) -> list[SchedulesIssue]:
    issues_list = []

    prev_lesson = lessons_sequence[0]
    for curr_lesson in lessons_sequence[1:]:
        # print(curr_lesson.start_time - prev_lesson.end_time)
        if timedelta(seconds=60*30) \
           < (curr_lesson.start_time - prev_lesson.end_time) \
           < timedelta(seconds=3600*9):
            # print("Found issue")
            issues_list.append(SchedulesIssue(
                0,
                prev_lesson,
                curr_lesson
            ))

        prev_lesson = curr_lesson

    return issues_list

def get_jogging_issues(lessons_sequence: list[Lesson]) -> list[SchedulesIssue]:
    issues_list = []

    def has_big_distance(lesson1: Lesson, lesson2: Lesson) -> bool:
        return False

    prev_lesson = lessons_sequence[0]
    for curr_lesson in lessons_sequence[1:]:
        # print(curr_lesson.start_time - prev_lesson.end_time)
        if has_big_distance(prev_lesson, curr_lesson):
            # print("Found issue")
            issues_list.append(SchedulesIssue(
                1,
                prev_lesson,
                curr_lesson
            ))

        prev_lesson = curr_lesson

    return issues_list

def get_insomnia_issues(lessons_sequence: list[Lesson]) -> list[SchedulesIssue]:
    issues_list = []

    prev_lesson = lessons_sequence[0]
    for curr_lesson in lessons_sequence[1:]:
        # print(curr_lesson.start_time - prev_lesson.end_time)
        if prev_lesson.end_time.time() > time(hour=20) and \
           curr_lesson.start_time.time() < time(hour=10):
            # print("Found issue")
            issues_list.append(SchedulesIssue(
                2,
                prev_lesson,
                curr_lesson
            ))

        prev_lesson = curr_lesson

    return issues_list


async def main():
    search_res = await get_search_json("ИКБО-70-24")
    # search_res = await get_search_json("Задерновский")
    cal = await get_calendar(search_res)
    lessons_sequence = await get_lessons_sequence(cal)

    lessons_sequence = [
        Lesson(
            "Py",
            "loc",
            datetime(2025, 2, 1, 20, 0, 0, 0),
            datetime(2025, 2, 1, 21, 0, 0, 0)
        ),
        Lesson(
            "Pu",
            "loc",
            datetime(2025, 2, 2, 9, 0, 0, 0),
            datetime(2025, 2, 2, 10, 0, 0, 0)
        )
    ]

    issues_list = get_insomnia_issues(lessons_sequence)
    for issue in issues_list:
        print(issue.first_lesson.name)
        print(issue.first_lesson.start_time)
        print(issue.second_lesson.name)
        print(issue.second_lesson.start_time)

if __name__ == "__main__":
    asyncio.run(main())