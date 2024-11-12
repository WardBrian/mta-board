import datetime as dt

class Dates:
    def __init__(self, config):
        self.important_dates = []
        for (event, date) in config.events:
            self.__add_date(event, date)

    def next_important_date_string(self):
        today = dt.date.today()
        try:
            date = self.next_important_date()
        except Exception:
            return ""
        days = (date["date"] - today).days
        plural = 's' if days > 1 else ''
        return f"{days} day{plural} until {date['text']}!"

    def next_important_date(self):
        today = dt.date.today()
        return min(
            filter(lambda d: d['date'] > today, self.important_dates),
            key=lambda d: d['date']
        )

    def __add_date(self, text, date):
        if date != "":
            self.important_dates.append({"text": text, "date": dt.date.fromisoformat(date)})
