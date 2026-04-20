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
        self.scrolling_speed = config.scrolling_speed

        self.scrolls = -1
        self.start = 0
        self.stops_per_page = layout.coords("trains").get("stops_per_page", 2)

        self.offset = layout.coords("trains")["offset"]

        self.bg = colors.graphics_color("default.background")

        self.eta_coords = layout.coords("trains.eta")
        self.eta_font = layout.font("trains.eta")
        self.eta_color = colors.graphics_color("trains.eta")

        self.stop_coords = layout.coords("trains.stop")
        self.stop_font = layout.font("trains.stop")
        self.stop_color = colors.graphics_color("trains.stop")

        self.line_coords = layout.coords("trains.line")
        self.line_font = layout.font("trains.line")

    def wait_time(self) -> float:
        return self.scrolling_speed

    def can_render(self, data: Trains) -> bool:
        return bool(data.stops)

    def render(self, data: Trains, canvas: "Canvas", graphics, scrolling_text_pos: int) -> None:
        stops = len(data.stops)
        if scrolling_text_pos == canvas.width:
            self.scrolls += 1
            if self.scrolls and self.scrolls % 2 == 0:
                self.start += self.stops_per_page
                if self.start >= stops:
                    self.start = 0
                LOGGER.debug("Moving to trains starting at stop %d", self.start)

        end = min(self.start + self.stops_per_page, stops)
        return self.__render_trains(canvas, graphics, data, self.start, end, scrolling_text_pos)

    def __render_trains(self, canvas: "Canvas", graphics, trains: Trains, first_stop, last_stop, text_pos):
        canvas.Fill(self.bg.red, self.bg.green, self.bg.blue)

        offset = 0
        position = 0
        for t in range(first_stop, last_stop):
            stop = trains.stops[t]
            pos = self.__render_stop(canvas, graphics, offset, stop, text_pos)
            position = max(pos, position)
            offset += self.offset

        return position

    def __render_stop(self, canvas, graphics, offset, stop: Stop, text_pos):

        graphics.DrawText(
            canvas,
            self.eta_font["font"],
            self.eta_coords["x"],
            self.eta_coords["y"] + offset,
            self.eta_color,
            stop.next_trains_string(),
        )

        pos = scrolling_text(
            canvas,
            graphics,
            self.stop_coords["x"],
            self.stop_coords["y"] + offset,
            self.stop_coords["width"],
            self.stop_font,
            self.stop_color,
            self.bg,
            stop.stop_name(),
            text_pos,
        )

        render_line(
            canvas,
            graphics,
            self.line_font,
            self.line_coords["x"],
            self.line_coords["y"] + offset,
            self.line_coords["radius"],
            stop.route,
        )
        return pos


def render_line(canvas, graphics, font, x, y, d, name):

    line_color = routes.ROUTE_COLOR[name]
    if routes.ROUTE_TYPE[name] == "train":
        DrawFilledCircle(canvas, x, y, d, line_color)
    else:
        DrawFilledRectangle(
            canvas, x - font["size"]["width"], y - d // 2 + 1, font["size"]["width"] * 2 + 1, d - 1, line_color
        )
    display_name = routes.ROUTE_NAME[name]
    text_x = center_text_position(display_name, x + 1, font["size"]["width"])
    color = graphics.Color(255, 255, 255)
    graphics.DrawText(canvas, font["font"], text_x, y + font["size"]["height"] // 2 - 1, color, display_name)


def DrawFilledCircle(canvas: "Canvas", x, y, d, color):
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


def DrawFilledRectangle(canvas: "Canvas", x, y, width, height, color):
    for xi in range(x, x + width):
        for yi in range(y, y + height):
            canvas.SetPixel(xi, yi, *color)
