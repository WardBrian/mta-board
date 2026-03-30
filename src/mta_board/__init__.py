from .config import Config
from .trains import Trains
from .renderer import Renderer


def load() -> tuple[type[Config], type[Trains], type[Renderer]]:
    return Config, Trains, Renderer
