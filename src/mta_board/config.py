import bullpen.api as api


class Config(api.PluginConfig):
    def __init__(self, config: api.MLBConfig) -> None:
        self.scrolling_speed = config.scrolling_speed

        self.routes = config.plugin_config.get("stops", {"6": ["631N"]}).items()
        self.skip_next = config.plugin_config.get("skip_next_trains", 0)
        self.num_trains = config.plugin_config.get("num_trains", 3)
