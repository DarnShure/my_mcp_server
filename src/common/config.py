
import toml
import os
import shutil
from typing import TypeVar, Any, Dict

T = TypeVar('T')


class ChatbotAPIConfig:
    _instance = None
    config: Dict[str, Any] = {}


def set_config_path(filename: str = ''):

    api_config = ChatbotAPIConfig
    api_config.config = toml.load(filename)
    version = api_config.config["api"]["version"]

    if os.path.exists('config/custom_config.toml'):
        custom_config = toml.load('config/custom_config.toml')
        api_config.config = update_nested_dict(api_config.config, custom_config)
        api_config.config["api"]["version"] = version

    else:
        shutil.copy('config/config.toml', 'config/custom_config.toml')


def get_config():
    api_config = ChatbotAPIConfig
    return api_config.config


def update_nested_dict(default, custom):
    result = default.copy()

    for key, value in custom.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = update_nested_dict(result[key], value)
        else:
            result[key] = value
    return result


def get_config_value(keys: list[str], default: Any):
    '''
    Since the config is a nested dictionary, this function is used to get the value of a key in the config.
    '''
    # global __config
    config = ChatbotAPIConfig.config
    for key in keys:
        if key in config:
            config = config[key]
        else:
            return default

    # check if the type of the value is the same as the default value
    if type(config) != type(default):
        raise ValueError(f'Expected type {type(default)} for {keys}, but got {type(config)}')
    return config


# try:
#     set_config_path('config/config.toml')
# except FileNotFoundError:
#     pass
