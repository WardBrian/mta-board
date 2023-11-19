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
        return trains, trains.update(True)

    def __init__(self, config: Config):
        self.starttime = time.time()
        self.routes = config.routes
        self.api = config.trains_apikey
        self.skip = config.skip_next
        self.num_trains = config.num_trains
        self.stops = []

    def update(self, force: bool = False):
        if force or self.__should_update():
            debug.log("Trains should update!")
            self.starttime = time.time()
            _stops = []
            failed = False
            for (route, stations) in self.routes:
                d = {}
                try:
                    feed = SubwayFeed.get(route, api_key=self.api)
                    try:
                        d = feed.extract_stop_dict().get(route, {})
                    except:
                        debug.exception("Serialization error while refreshing train data")
                except:
                    debug.exception("Networking Error while refreshing train data")
                    failed = True

                _stops += [Stop(route, stop, sorted(d.get(stop, [])), self.skip, self.num_trains) for stop in stations]

            self.stops = _stops

            if failed:
                return UpdateStatus.FAIL

            return UpdateStatus.SUCCESS

        return UpdateStatus.DEFERRED

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= TRAINS_UPDATE_RATE

    def __str__(self):
        trains = "\n\t".join(str(s) for s in self.stops)
        return "Trains: \n\t" + trains


class Stop:
    def __init__(self, route, stop, trains, skip, num_show):
        self.route = route
        self.stop = stop
        self.trains = trains
        self.skip = max(skip, 0)
        self.num_show = max(num_show, 1)

    def stop_name(self):
        return stops.name(self.stop)

    def format_time(self, minutes: int, num_show: int):
        if num_show == 1:
            if minutes == 0:
                return " Arriving"
            return f"{minutes: 2} minute{'s' if minutes > 1 else ''}"

        if minutes == 0:
            return "Arr"
        return f"{minutes}m"

    def next_train(self):
        now = datetime.now(tz=get_localzone())
        times = []
        try:
            i = self.skip
            while len(times) < self.num_show:
                train = self.trains[i]
                delta = train - now
                i += 1
                if delta.days < 0:
                    continue
                minutes = (delta.seconds + 30) // 60
                times.append(minutes)
        except:
            pass

        n_times = len(times)
        if not n_times:
            return " Not Running"

        return (" " if n_times != 1 else "") + (", ".join(self.format_time(t, len(times)) for t in times))

    def __str__(self):
        return f"{self.route}:{self.stop_name()}:{self.next_train()}"
