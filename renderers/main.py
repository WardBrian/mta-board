import time
from typing import Callable, NoReturn

import debug
from data import Data
from renderers import network, trains, weather


class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data: Data = data
        self.canvas = matrix.CreateFrameCanvas()
        self.scrolling_text_pos = self.canvas.width
        self.animation_time = 0

    def render(self) -> NoReturn:
        while True:
            self.__render_weather(scrolling_finished_cond(self.data))
            self.__render_trains()

    def __render_trains(self):
        debug.info(self.data.trains)
        stops = len(self.data.trains.stops)
        stops_per_page = self.data.config.layout.coords("trains")["stops_per_page"]
        for start in range(0, stops + stops_per_page - 1, stops_per_page):
            batch = slice(start, min(start + stops_per_page, stops))
            self.__render_train_batch(any_of(timer_cond(45), scrolling_finished_cond(self.data)), batch)

    def __render_train_batch(self, cond, batch):

        self.data.scrolling_finished = False
        self.scrolling_text_pos = self.canvas.width

        while cond():
            pos = trains.render_trains(
                self.canvas,
                self.data.config.layout,
                self.data.config.scoreboard_colors,
                self.data.trains.stops[batch],
                self.scrolling_text_pos,
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)

            # Show network issues
            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(self.data.config.scrolling_speed)

    # Render an offday screen with the weather, clock and news
    def __render_weather(self, cond):
        self.data.scrolling_finished = False
        self.scrolling_text_pos = self.canvas.width

        while cond():

            self.__max_scroll_x(self.data.config.layout.coords("offday.scrolling_text"))
            pos = weather.render_weather_screen(
                self.canvas,
                self.data.config.layout,
                self.data.config.scoreboard_colors,
                self.data.weather,
                self.data.dates,
                self.data.config.time_format,
                self.scrolling_text_pos,
            )
            self.__update_scrolling_text_pos(pos, self.canvas.width)
            # Show network issues
            if self.data.network_issues:
                network.render_network_error(self.canvas, self.data.config.layout, self.data.config.scoreboard_colors)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(self.data.config.scrolling_speed)

    def __max_scroll_x(self, scroll_coords):
        scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
        self.scrolling_text_pos = min(scroll_max_x, self.scrolling_text_pos)

    def __update_scrolling_text_pos(self, new_pos, end):
        """Updates the position of the probable starting pitcher text."""
        pos_after_scroll = self.scrolling_text_pos - 1
        if pos_after_scroll + new_pos < -4:
            self.data.scrolling_finished = True
            self.scrolling_text_pos = end
        else:
            self.data.scrolling_finished = False
            self.scrolling_text_pos = pos_after_scroll


def timer_cond(seconds) -> Callable[[], bool]:
    """Create a condition that is true for the specified number of seconds"""
    end = time.time() + seconds

    def cond():
        return time.time() < end

    return cond


def scrolling_finished_cond(data: Data) -> Callable[[], bool]:
    """Create a condition that is true when scrolling is finished"""

    def cond():
        return not data.scrolling_finished

    return cond


def any_of(*conds) -> Callable[[], bool]:
    """Create a condition that is true if any of the given conditions are true"""

    def cond():
        return any(c() for c in conds)

    return cond
