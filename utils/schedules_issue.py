from utils.lesson import Lesson


class SchedulesIssue:
    issues_types = [
        "Окно между парами",
        "Большое расстояние между аудиториями",
        "Пары поздно заканчиваются, а завтра рано вставать",
    ]

    def __init__(self, type_id: int, first_lesson: Lesson, second_lesson: Lesson):
        self.type_id = type_id
        self.desc = SchedulesIssue.issues_types[type_id]
        self.first_lesson = first_lesson
        self.second_lesson = second_lesson

    def formatted(self):
        return {
            "type_id": self.type_id,
            "description": self.desc,
            "first_lesson_title": self.first_lesson.name,
            "second_lesson_title": self.second_lesson.name,
            "date": self.first_lesson.start_time.strftime('%Y-%m-%d'),
            "week_day": self.first_lesson.start_time.weekday(),
        }