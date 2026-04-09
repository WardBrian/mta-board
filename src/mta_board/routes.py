from PIL import ImageColor

from importlib.resources import files


with files("mta_board").joinpath("routes.csv").open("r") as f:
    f.readline()
    _routes = f.readlines()

_routes = [line.strip().split(",") for line in _routes]

ROUTE_NAME = {r[0]: r[1] for r in _routes}
ROUTE_COLOR = {r[0]: ImageColor.getcolor("#" + (r[3] or "858585"), "RGB") for r in _routes}
ROUTE_TYPE = {r[0]: r[4] for r in _routes}

del _routes
