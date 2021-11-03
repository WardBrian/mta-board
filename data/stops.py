with open("data/stops.txt", "r") as f:
    f.readline()
    _stops = f.readlines()

_stops = [line.split(",") for line in _stops]

ID_STOPS = {stop[0]: stop[2] for stop in _stops}
del _stops


def name(stop: str):
    try:
        name = ID_STOPS[stop]
    except KeyError:
        return "Unknown"
    else:
        if stop.endswith("S"):
            return name + " DWN"
        elif stop.endswith("N"):
            return name + " UP"
        else:
            return name


def get(route, stop):
    for key, value in ID_STOPS.items():
        if key.startswith(route) and value == stop:
            return key
    return None
