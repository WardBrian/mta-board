import time
from datetime import datetime

from tzlocal import get_localzone
from bullpen.api import UpdateStatus, PluginData
from bullpen.logging import LOGGER
from underground import SubwayFeed


from . import routes, stops
from .config import Config

TRAINS_UPDATE_RATE = 180


class Trains(PluginData):

    def __init__(self, config: Config):
        self.starttime = time.time()
        self.routes = config.routes
        self.skip = config.skip_next
        self.num_trains = config.num_trains
        self.stops = []
        self.update(True)

    def update(self, force: bool = False):
        if force or self.__should_update():
            LOGGER.debug("Trains should update!")
            _stops = []
            failed = False

            seen = set()
            for route, stations in self.routes:
                if route in seen:
                    continue
                seen.add(route)

                data = {}

                if routes.ROUTE_TYPE[route] == "train":
                    failed, data = _get_feed(route)

                    d = data.get(route, {})
                    for stop in stations:
                        _stops.append(Stop(route, stop, sorted(d.get(stop, [])), self.skip, self.num_trains))
                else:
                    failed, data = _get_feed("BUS")
                    # optimization: buses share the same feed, so don't load it a bunch of times!
                    for route, stations in self.routes:
                        if routes.ROUTE_TYPE[route] == "bus":
                            seen.add(route)
                            d = data.get(route, {})
                            for stop in stations:
                                _stops.append(Stop(route, stop, sorted(d.get(stop, [])), self.skip, self.num_trains))

            self.stops = _stops

            LOGGER.debug("Updated trains!")
            self.starttime = time.time()
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


def _get_feed(route):
    try:
        feed = SubwayFeed.get(route)
        try:
            return False, feed.extract_stop_dict()
        except:
            LOGGER.exception("Serialization error while refreshing train data")
    except:
        LOGGER.exception("Networking Error while refreshing train data")
        return True, {}


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

    def next_trains_string(self):
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
        return f"{self.route}:{self.stop_name()}:{self.next_trains_string()}"
