import json

class Trend:
    def __init__(self, file):
        self.file = file

    async def get_trend(self, param: str, new_trend: str = ''):
        with open(self.file, "r") as json_data:
            trend = json.load(json_data)
            if param == "r":
                return trend['trend']
            elif param == "w":
                trend['trend'] = new_trend
                await self.update_trend(trend)

    async def update_trend(self, new_data):
        with open(self.file, "w") as json_data:
            json.dump(new_data, json_data, indent=2)

class Ignore_words:
    def __init__(self, file):
        self.file = file

    async def get_ignore_words(self, param: str, new_word: str = '', index: int = 0):
        with open(self.file, "r") as json_data:
            trend = json.load(json_data)
            if param == "r":
                return trend['ignore_words']
            elif param == "w":
                trend['ignore_words'].append(new_word)
            elif param == "d":
                trend['ignore_words'].pop(index)
            await self.update_ignore_words(trend)

    async def update_ignore_words(self, new_data):
        with open(self.file, "w") as json_data:
            json.dump(new_data, json_data, indent=2)