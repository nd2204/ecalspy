from ecalspy.core.es_utils import JsonSerializer, FileExists

import os

class EsConfigManager:
    __Config = {}
    __AutoFlush = True
    __Loaded = False

    CONFIG_FILENAME = "conf.json"

    @staticmethod
    def EnsureLoaded():
        if not EsConfigManager.__Loaded:
            EsConfigManager.LoadConfigsFromFile()

    @staticmethod
    def LoadConfigsFromFile(name=CONFIG_FILENAME) -> None:
        # make sure the config is flushed when reloading
        if EsConfigManager.__Loaded:
            EsConfigManager.FlushConfig()
            return

        if not FileExists(name):
            EsConfigManager.FlushConfig()
        else:
            with open(name, "r") as fp:
                EsConfigManager.__Config = JsonSerializer.DeserializeFile(fp, False)

        EsConfigManager.__Loaded = True


    @staticmethod
    def PushConfig(key, value) -> None:
        assert EsConfigManager.__Loaded

        EsConfigManager.__Config[key] = value
        if EsConfigManager.__AutoFlush:
            EsConfigManager.FlushConfig()

    @staticmethod
    def GetConfig(key) -> object:
        assert EsConfigManager.__Loaded

        if key in EsConfigManager.__Config:
            return EsConfigManager.__Config[key]
        else:
            return None

    @staticmethod
    def FlushConfig():
        assert EsConfigManager.__Loaded

        with open(EsConfigManager.CONFIG_FILENAME, "w") as fp:
            fp.write(JsonSerializer.Serialize(EsConfigManager.__Config, False))

    @staticmethod
    def SetAutoFlush(enable: bool):
        assert EsConfigManager.__Loaded

        EsConfigManager.__AutoFlush = enable
