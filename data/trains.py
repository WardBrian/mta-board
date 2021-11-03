import time
from datetime import datetime

from tzlocal import get_localzone
from underground import SubwayFeed

import debug
from data import stops
from data.config import Config
from data.update import UpdateStatus

TRAINS_UPDATE_RATE = 60


class Trains:
    @staticmethod
    def get_trains(config):
        trains = Trains(config)
        if trains.update(True) == UpdateStatus.SUCCESS:
            return trains
        return None

    def __init__(self, config: Config):
        self.starttime = time.time()
        self.routes = config.routes
        self.api = config.trains_apikey
        self.skip = config.skip_next
        self.stops = []

    def update(self, force: bool = False):
        if force or self.__should_update():
            debug.log("Trains should update!")
            self.starttime = time.time()
            try:
                _stops = []
                for (route, stations) in self.routes:
                    feed = SubwayFeed.get(route, api_key=self.api)

                    d = feed.extract_stop_dict().get(route, {})
                    _stops += [Stop(route, stop, d.get(stop, []), self.skip) for stop in stations]

                self.stops = _stops

                return UpdateStatus.SUCCESS
            except:
                debug.exception("Networking Error while refreshing train data")
                return UpdateStatus.FAIL
        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= TRAINS_UPDATE_RATE


class Stop:
    def __init__(self, route, stop, trains, skip):
        self.route = route
        self.stop = stop
        self.trains = trains
        self.skip = max(skip, 0)

    def stop_name(self):
        return stops.name(self.stop)

    def next_train(self):
        now = datetime.now(tz=get_localzone())
        try:
            delta = self.trains[self.skip] - now
            if delta.days < 0:
                delta = self.trains[self.skip + 1] - now
            minutes = delta.seconds // 60
            if minutes:
                return f"{minutes: 2} minute{'s' if minutes > 1 else ''}"
            else:
                return " Arriving"
        except:
            return " Not Running"

    def __str__(self):
        return f"{self.route}:{self.stop_name()}:{self.next_train()}"
