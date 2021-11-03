import json
import os
import sys

import debug
from data.config.color import Color
from data.config.layout import Layout
from utils import deep_update

SCROLLING_SPEEDS = [0.3, 0.2, 0.1, 0.075, 0.05, 0.025, 0.01]
DEFAULT_SCROLLING_SPEED = 2


class Config:
    def __init__(self, filename_base, width, height):
        json = self.__get_config(filename_base)

        # News Ticker
        self.news_ticker_countdowns = json["news_ticker"]["countdowns"]
        self.news_ticker_date = json["news_ticker"]["date"]
        self.news_ticker_date_format = json["news_ticker"]["date_format"]
        self.events = [(e["event"], e["date"]) for e in json["news_ticker"]["events"]]

        # Rotation

        self.trains_apikey = json["trains"]["apikey"]
        self.routes = json["trains"]["stops"].items()
        self.skip_next = json["trains"]["skip_next_trains"]

        # Weather
        self.weather_apikey = json["weather"]["apikey"]
        self.weather_location = json["weather"]["location"]
        self.weather_metric_units = json["weather"]["metric_units"]

        # Misc config options
        self.time_format = json["time_format"]

        self.debug = json["debug"]

        # Get the layout info
        json = self.__get_layout(width, height)
        self.layout = Layout(json, width, height)

        json = self.__get_colors("scoreboard")  # TODO
        self.scoreboard_colors = Color(json)

        try:
            self.scrolling_speed = SCROLLING_SPEEDS[json["scrolling_speed"]]
        except:
            debug.warning(
                "Scrolling speed should be an integer between 0 and 6. Using default value of {}".format(
                    DEFAULT_SCROLLING_SPEED
                )
            )
            self.scrolling_speed = SCROLLING_SPEEDS[DEFAULT_SCROLLING_SPEED]

        # Check the preferred teams and divisions are a list or a string
        self.check_time_format()

        # # Check the rotation_rates to make sure it's valid and not silly

    def check_time_format(self):
        if self.time_format.lower() == "24h":
            self.time_format = "%H"
        else:
            self.time_format = "%I"

    def read_json(self, path):
        """
        Read a file expected to contain valid json.
        If file not present return empty data.
        Exception if json invalid.
        """
        j = {}
        if os.path.isfile(path):
            j = json.load(open(path))
        else:
            debug.warning(f"Could not find json file {path}.  Skipping.")
        return j

    # example config is a "base config" which always gets read.
    # our "custom" config contains overrides.
    def __get_config(self, base_filename):
        filename = "{}.json".format(base_filename)
        reference_filename = "config.json.example"  # always use this filename.
        reference_config = self.read_json(reference_filename)
        custom_config = self.read_json(filename)
        if custom_config:
            new_config = deep_update(reference_config, custom_config)
            return new_config
        return reference_config

    def __get_colors(self, base_filename):
        filename = "colors/{}.json".format(base_filename)
        reference_filename = "{}.example".format(filename)
        reference_colors = self.read_json(reference_filename)
        if not reference_colors:
            debug.error(
                "Invalid {} reference color file. Make sure {} exists in colors/".format(base_filename, base_filename)
            )
            sys.exit(1)

        custom_colors = self.read_json(filename)
        if custom_colors:
            debug.info("Custom '%s.json' colors found. Merging with default reference colors.", base_filename)
            new_colors = deep_update(reference_colors, custom_colors)
            return new_colors
        return reference_colors

    def __get_layout(self, width, height):
        filename = "coordinates/w{}h{}.json".format(width, height)
        reference_filename = "{}.example".format(filename)
        reference_layout = self.read_json(reference_filename)
        if not reference_layout:
            # Unsupported coordinates
            debug.error(
                "Invalid matrix dimensions provided. See top of README for supported dimensions."
                "\nIf you would like to see new dimensions supported, please file an issue on GitHub!"
            )
            sys.exit(1)

        # Load and merge any layout customizations
        custom_layout = self.read_json(filename)
        if custom_layout:
            debug.info("Custom '%dx%d.json' found. Merging with default reference layout.", width, height)
            new_layout = deep_update(reference_layout, custom_layout)
            return new_layout
        return reference_layout
