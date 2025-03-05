from .lesson import Lesson


class ScheduleIssue:
    # issues_types = [
    #     "Окно между парами",
    #     "Большое расстояние между аудиториями",
    #     "Пары поздно заканчиваются, а завтра рано вставать",
    # ]

    def __init__(self, target_id: int, type_id: int, first_lesson: Lesson, second_lesson: Lesson):
        self.target_id = target_id
        self.type_id = type_id
        self.first_lesson = first_lesson
        self.second_lesson = second_lesson

    def formatted(self):
        return {
            "target_id": self.target_id,
            "type_id": self.type_id,
            "first_lesson_title": self.first_lesson.name,
            "second_lesson_title": self.second_lesson.name,
            "first_lesson_dt": self.first_lesson.start_time,
            "second_lesson_dt": self.second_lesson.start_time,
        }