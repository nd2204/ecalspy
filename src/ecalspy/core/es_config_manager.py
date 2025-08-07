from ecalspy.core.es_utils import JsonSerializer, FileExists

import os

from pprint import pprint
from json.decoder import JSONDecodeError

class ConfigManager:
    __Config = {}
    __AutoFlush = True
    __Loaded = False

    CONFIG_FILENAME = "conf.json"

    @staticmethod
    def EnsureLoaded():
        if not ConfigManager.__Loaded:
            ConfigManager.LoadConfigsFromFile()

    @staticmethod
    def LoadConfigsFromFile(name=CONFIG_FILENAME) -> None:
        # make sure the config is flushed when reloading
        if ConfigManager.__Loaded:
            ConfigManager.FlushConfig()
            return

        if not FileExists(name):
            ConfigManager.FlushConfig()
        else:
            with open(name, "r") as fp:
                try:
                    ConfigManager.__Config = JsonSerializer.DeserializeFile(fp, False)
                except JSONDecodeError:
                    pass

        ConfigManager.__Loaded = True


    @staticmethod
    def PushConfig(key: str, value: object) -> None:
        ConfigManager.EnsureLoaded()

        keys = key.split(".")
        current = ConfigManager.__Config
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                current[k] = {}

        current[keys[-1]] = value

        if ConfigManager.__AutoFlush:
            ConfigManager.FlushConfig()

    @staticmethod
    def GetConfig(key: str) -> object:
        ConfigManager.EnsureLoaded()

        keys = [k.strip() for k in key.split(".")]
        current = ConfigManager.__Config

        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        if key in current:
            return current[key]
        else:
            return None

    @staticmethod
    def CreateOrRetrieveConfig(key: str, valueOnCreate: object = "") -> None:
        result = ConfigManager.GetConfig(key)
        if not result:
            ConfigManager.PushConfig(key, valueOnCreate)
            return valueOnCreate
        return result

    @staticmethod
    def FlushConfig():
        assert ConfigManager.__Loaded

        with open(ConfigManager.CONFIG_FILENAME, "w") as fp:
            fp.write(JsonSerializer.Serialize(ConfigManager.__Config, False))

    @staticmethod
    def SetAutoFlush(enable: bool):
        ConfigManager.__AutoFlush = enable
