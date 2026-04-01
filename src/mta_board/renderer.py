from typing import TYPE_CHECKING

from bullpen.api import Layout, Color, PluginRenderer
from bullpen.util import center_text_position, scrolling_text
from bullpen.logging import LOGGER

from .config import Config
from .trains import Stop, Trains
from . import routes


if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas


class Renderer(PluginRenderer):
    def __init__(self, config: Config, layout: Layout, colors: Color) -> None:
        self.config = config
        self.layout = layout
        self.colors = colors

        self.scrolls = -1
        self.start = 0
        self.stops_per_page = layout.coords("trains").get("stops_per_page", 2)

    def wait_time(self) -> float:
        return self.config.scrolling_speed

    def can_render(self, data: Trains) -> bool:
        return bool(data.stops)

    def render(self, data: Trains, canvas: "Canvas", graphics, scrolling_text_pos: int) -> None:
        stops = len(data.stops)
        if scrolling_text_pos == canvas.width:
            self.scrolls += 1
            if self.scrolls and self.scrolls % 2 == 0:
                self.start += self.stops_per_page
                if self.start > stops:
                    self.start = 0
                LOGGER.debug("Moving to trains starting at stop %d", self.start)

        end = min(self.start + self.stops_per_page, stops)
        return render_trains(canvas, graphics, self.layout, self.colors, data, self.start, end, scrolling_text_pos)


def render_trains(canvas, graphics, layout: Layout, colors: Color, trains: Trains, first_stop, last_stop, text_pos):
    color = colors.color("default.background")
    canvas.Fill(color["r"], color["g"], color["b"])

    offset = 0
    positions = []
    for t in range(first_stop, last_stop):
        stop = trains.stops[t]
        pos, new_offset = __render_stop(canvas, graphics, layout, colors, offset, stop, text_pos)
        offset += new_offset
        positions.append(pos)

    return max(positions)


def __render_stop(canvas, graphics, layout, colors, offset, stop: Stop, text_pos):
    coords = layout.coords("trains.eta")
    font = layout.font("trains.eta")
    color = graphics.Color(255, 255, 255)
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"] + offset, color, stop.next_train())

    coords = layout.coords("trains.stop")
    font = layout.font("trains.stop")
    name = stop.stop_name()
    bgcolor = colors.graphics_color("default.background")

    pos = scrolling_text(
        canvas, graphics, coords["x"], coords["y"] + offset, coords["width"], font, color, bgcolor, name, text_pos
    )

    coords = layout.coords("trains.line")
    __render_line(
        canvas, graphics, layout.font("trains.line"), coords["x"], coords["y"] + offset, coords["radius"], stop.route
    )
    return pos, layout.coords("trains")["offset"]


def __render_line(canvas, graphics, font, x, y, d, name):

    color = routes.ROUTE_COLOR[name]
    if routes.ROUTE_TYPE[name] == "train":
        DrawFilledCircle(canvas, x, y, d, color)
    else:
        DrawFilledRectangle(
            canvas, x - font["size"]["width"], y - d // 2 + 1, font["size"]["width"] * 2 + 1, d - 1, color
        )
    display_name = routes.ROUTE_NAME[name]
    text_x = center_text_position(display_name, x + 1, font["size"]["width"])
    color = graphics.Color(255, 255, 255)
    graphics.DrawText(canvas, font["font"], text_x, y + font["size"]["height"] // 2 - 1, color, display_name)


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


def DrawFilledRectangle(canvas, x, y, width, height, color):
    for xi in range(x, x + width):
        for yi in range(y, y + height):
            canvas.SetPixel(xi, yi, *color)
