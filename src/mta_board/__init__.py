from bullpen import api
from .config import Config
from .trains import Trains
from .renderer import Renderer


def load() -> api.PLUGIN_DEFINITION:
    return Config, Trains, Renderer
