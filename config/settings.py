from pathlib import Path
import yaml


def load_config(filename="config.yml"):
    path_to_config = Path(__file__).parent.joinpath(filename)
    with open(path_to_config) as f:
        config = yaml.safe_load(f)
    return config


_local_config = load_config("local.config.yml")


class PathConfig:
    def __init__(self):
        self._config = _local_config

    @property
    def path_to_etf_data(self):
        return self._config["path"]["sp_etf_data"]
