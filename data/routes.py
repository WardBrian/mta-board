from PIL import ImageColor

with open("data/routes.txt", "r") as f:
    f.readline()
    _routes = f.readlines()

_routes = [line.split(",") for line in _routes]

ROUTE_COLOR = {r[0]: ImageColor.getcolor("#" + (r[-2] or "858585"), "RGB") for r in _routes}
ROUTE_NAME = {r[0]: r[3] for r in _routes}

del _routes
