from json import JSONEncoder, JSONDecoder

class GameEncoder(JSONEncoder):
    def default(self, o):
            return o.__dict__

class JSONUtility:
    def encode(obj):
        return GameEncoder().encode(obj)

    def decode(str):
        return JSONDecoder().decode(s=str)