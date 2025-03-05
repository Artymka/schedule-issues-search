import asyncio
import icalendar
from datetime import datetime, time, timedelta
from functools import cmp_to_key

from utils.utils import get_search_json, get_calendar, get_lessons_sequence
from utils.lesson import Lesson
from utils.schedule_issue import ScheduleIssue


def search_window_issues(lessons_sequence: list[Lesson], target_id: int) -> list[ScheduleIssue]:
    issues_list = []

    prev_lesson = lessons_sequence[0]
    for curr_lesson in lessons_sequence[1:]:
        # print(curr_lesson.start_time - prev_lesson.end_time)
        if timedelta(seconds=60*30) \
           < (curr_lesson.start_time - prev_lesson.end_time) \
           < timedelta(seconds=3600*9):
            # print("Found issue")
            issues_list.append(ScheduleIssue(
                target_id,
                0,
                prev_lesson,
                curr_lesson
            ))

        prev_lesson = curr_lesson

    return issues_list

def search_jogging_issues(lessons_sequence: list[Lesson], target_id: int) -> list[ScheduleIssue]:
    issues_list = []

    def has_big_distance(lesson1: Lesson, lesson2: Lesson) -> bool:
        if not lesson1.room or not lesson2.room: return False
        sweet_pairs = [
            ["Д", "И"],
            ["ФОК", "И"],
            ["Е", "И"],
        ]

        for pair in sweet_pairs:
            if pair[0] in lesson1.room and \
               pair[1] in lesson2.room or \
               pair[1] in lesson1.room and \
               pair[0] in lesson2.room:
                return True
        return False

    prev_lesson = lessons_sequence[0]
    for curr_lesson in lessons_sequence[1:]:
        if curr_lesson.start_time - prev_lesson.end_time == timedelta(minutes=10) and \
           has_big_distance(prev_lesson, curr_lesson):
            issues_list.append(ScheduleIssue(
                target_id,
                1,
                prev_lesson,
                curr_lesson
            ))

        prev_lesson = curr_lesson

    return issues_list

def search_insomnia_issues(lessons_sequence: list[Lesson], target_id: int) -> list[ScheduleIssue]:
    issues_list = []

    prev_lesson = lessons_sequence[0]
    for curr_lesson in lessons_sequence[1:]:
        # print(curr_lesson.start_time - prev_lesson.end_time)
        if prev_lesson.end_time.time() > time(hour=20) and \
           curr_lesson.start_time.time() < time(hour=10):
            # print("Found issue")
            issues_list.append(ScheduleIssue(
                target_id,
                2,
                prev_lesson,
                curr_lesson
            ))

        prev_lesson = curr_lesson

    return issues_list

def search_all_issues(lessons_sequence: list[Lesson], target_id: int) -> list[ScheduleIssue]:
    if not lessons_sequence:
        return []

    res = []
    res += search_window_issues(lessons_sequence, target_id)
    res += search_jogging_issues(lessons_sequence, target_id)
    res += search_insomnia_issues(lessons_sequence, target_id)
    return res


async def main():
    search_res = await get_search_json("ИКБО-70-24")
    # search_res = await get_search_json("Задерновский")
    cal = await get_calendar(search_res)
    lessons_sequence = await get_lessons_sequence(cal)

    lessons_sequence = [
        Lesson(
            "Py",
            "И-214",
            datetime(2025, 2, 1, 20, 0, 0, 0),
            datetime(2025, 2, 1, 21, 0, 0, 0)
        ),
        Lesson(
            "Pu",
            "ФОК-5",
            datetime(2025, 2, 1, 21, 10, 0, 0),
            datetime(2025, 2, 1, 23, 0, 0, 0)
        )
    ]

    issues_list = search_jogging_issues(lessons_sequence)
    print("***", len(issues_list) > 0)

    for issue in issues_list:
        print(issue.first_lesson.name)
        print(issue.first_lesson.start_time)
        print(issue.second_lesson.name)
        print(issue.second_lesson.start_time)

if __name__ == "__main__":
    asyncio.run(main())