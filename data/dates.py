from datetime import datetime, timedelta


class Dates:
    def __init__(self, config):
        self.important_dates = []
        for (event, date) in config.events:
            self.__add_date(event, date)

    def next_important_date_string(self):
        today = datetime.today()
        date = self.next_important_date()
        days = (date["date"] - today).days
        return "{} days until {}!".format(days, date["text"])

    def next_important_date(self):
        today = datetime.today()
        return min(
            self.important_dates,
            key=lambda date: date["date"] - today if (date["date"] - today).days > 0 else timedelta.max,
        )

    def __add_date(self, text, date):
        if date != "":
            self.important_dates.append({"text": text, "date": datetime.strptime(date, "%Y-%m-%d")})
