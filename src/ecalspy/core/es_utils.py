import os
import json

class JsonSerializer:
    def Serialize(obj, encode=True):
        jsonStr = json.dumps(obj, indent=2, ensure_ascii=False)
        if encode:
            return jsonStr.encode('utf-8')
        return jsonStr

    def Deserialize(jsonStr, decode=True) -> object:
        obj = json.loads(jsonStr)
        if decode:
            return obj.decode('utf-8')
        return obj

    def DeserializeFile(fp, decode=True) -> object:
        obj = json.load(fp)
        if decode:
            return obj.decode('utf-8')
        return obj

def FileExists(name: str) -> bool:
    return os.access(name, os.F_OK)
