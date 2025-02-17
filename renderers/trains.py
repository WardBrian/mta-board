from driver import graphics

from data import routes
from data.config.color import Color
from data.config.layout import Layout
from data.trains import Stop, Trains
from utils import center_text_position


def render_trains(canvas, layout: Layout, colors: Color, trains: Trains):
    color = colors.color("default.background")
    canvas.Fill(color["r"], color["g"], color["b"])

    offset = 0
    for stop in trains.stops:
        offset += __render_stop(canvas, layout, offset, stop)


def __render_stop(canvas, layout, offset, stop: Stop):
    coords = layout.coords("trains.eta")
    font = layout.font("trains.eta")
    color = graphics.Color(255, 255, 255)
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"] + offset, color, stop.next_train())

    coords = layout.coords("trains.stop")
    font = layout.font("trains.stop")
    name = stop.stop_name()
    text_x = center_text_position(name, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"] + offset, color, name)

    coords = layout.coords("trains.line")
    __render_line(canvas, layout.font("trains.line"), coords["x"], coords["y"] + offset, coords["radius"], stop.route)
    return layout.coords("trains")["offset"]


def __render_line(canvas, font, x, y, d, name):

    color = routes.ROUTE_COLOR[name]
    DrawFilledCircle(canvas, x, y, d, color)
    text_x = center_text_position(name, x + 1, font["size"]["width"])
    color = graphics.Color(255, 255, 255)
    graphics.DrawText(canvas, font["font"], text_x, y + font["size"]["height"] // 2 - 1, color, name)


def DrawFilledCircle(canvas, x, y, d, color):
    ri = d // 2
    r = d / 2
    for xi in range(x - ri - 1, x + ri + 1):
        xi = int(xi)
        for yi in range(y - ri - 1, y + ri + 1):
            yi = int(yi)
            xd = xi - (x + 0.5)
            yd = yi - (y + 0.5)
            if xd * xd + yd * yd <= r * r:
                canvas.SetPixel(xi, yi, *color)
