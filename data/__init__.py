from data.dates import Dates
from data.trains import Trains
from data.update import UpdateStatus
from data.weather import Weather


class Data:
    def __init__(self, config):
        # Save the parsed config
        self.config = config

        self.weather: Weather = Weather(config)
        self.trains: Trains = Trains.get_trains(config)
        self.dates: Dates = Dates(config)

        # Network status state - we use headlines and weather condition as a sort of sentinial value
        self.network_issues: bool = (self.weather.conditions == "Error") or (not self.trains)

        # RENDER ITEMS
        self.scrolling_finished: bool = False

    def refresh_weather(self):
        self.__process_network_status(self.weather.update())

    def refresh_arrivals(self):
        self.__process_network_status(self.trains.update())

    def __process_network_status(self, status):
        if status == UpdateStatus.SUCCESS:
            self.network_issues = False
        elif status == UpdateStatus.FAIL:
            self.network_issues = True
