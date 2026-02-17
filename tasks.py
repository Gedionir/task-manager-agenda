class Task:
    def __init__(self, title, done=False, day=None, start_time=None, end_time=None):
        self.title = title
        self.done = done
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        status = "✔️" if self.done else "❌"
        day_str = self.day.strftime("%d/%m/%Y") if self.day else "Sem data"
        start_str = self.start_time.strftime("%H:%M") if self.start_time else "??:??"
        end_str = self.end_time.strftime("%H:%M") if self.end_time else "??:??"
        return f"{status} {self.title} - {day_str} {start_str} às {end_str}"