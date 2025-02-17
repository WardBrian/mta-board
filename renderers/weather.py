from driver import graphics

import time, os

from PIL import Image

from data.config.color import Color
from data.config.layout import Layout
from data.dates import Dates
from data.weather import Weather
from renderers import scrollingtext
from utils import center_text_position


def render_weather_screen(canvas, layout: Layout, colors: Color, weather: Weather, dates: Dates, time_format, text_pos):
    color = colors.color("default.background")
    canvas.Fill(color["r"], color["g"], color["b"])

    text_len = __render_news_ticker(canvas, layout, colors, dates, text_pos)
    __render_clock(canvas, layout, colors, time_format)
    __render_weather(canvas, layout, colors, weather)

    return text_len


def __render_clock(canvas, layout, colors, time_format):
    time_format_str = "{}:%M".format(time_format)
    if time_format == "%I":
        time_format_str += "%p"
    time_text = time.strftime(time_format_str)
    coords = layout.coords("offday.time")
    font = layout.font("offday.time")
    color = colors.graphics_color("offday.time")
    text_x = center_text_position(time_text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, time_text)


def __render_weather(canvas, layout, colors, weather: Weather):
    if weather.available():
        image_file = weather.icon_filename()
        try:
            weather_icon = Image.open(image_file)
        except Exception:
            pass
        else:
            __render_weather_icon(canvas, layout, colors, weather_icon)
            weather_icon.close()

        __render_weather_text(canvas, layout, colors, weather.conditions, "conditions")
        __render_weather_text(canvas, layout, colors, weather.temperature_string(), "temperature")
        __render_weather_text(canvas, layout, colors, weather.wind_speed_string(), "wind_speed")
        __render_weather_text(canvas, layout, colors, weather.wind_dir_string(), "wind_dir")
        __render_weather_text(canvas, layout, colors, weather.wind_string(), "wind")


def __render_weather_text(canvas, layout, colors, text, keyname):
    coords = layout.coords("offday.{}".format(keyname))
    font = layout.font("offday.{}".format(keyname))
    color = colors.graphics_color("offday.{}".format(keyname))
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)


def __render_weather_icon(canvas, layout, colors, weather_icon):
    coords = layout.coords("offday.weather_icon")
    color = colors.color("offday.weather_icon")
    resize = coords.get("rescale_icon")

    if resize:
        weather_icon = weather_icon.resize(
            (weather_icon.width * resize, weather_icon.height * resize), Image.NEAREST
        )
    for x in range(weather_icon.width):
        for y in range(weather_icon.height):
            pixel = weather_icon.getpixel((x, y))
            if pixel[3] > 0:
                canvas.SetPixel(coords["x"] + x, coords["y"] + y, color["r"], color["g"], color["b"])


def __render_news_ticker(canvas, layout, colors, date: Dates, text_pos):
    coords = layout.coords("offday.scrolling_text")
    font = layout.font("offday.scrolling_text")
    color = colors.graphics_color("offday.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    ticker_text = date.next_important_date_string()
    return scrollingtext.render_text(
        canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, ticker_text, text_pos
    )
