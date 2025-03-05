from datetime import datetime

class Lesson:
    def __init__(self, name: str, room: str, start_time: datetime, end_time: datetime):
        self.name = name
        self.room = room
        self.start_time = start_time
        self.end_time = end_time