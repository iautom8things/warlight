import uuid

class Player(object):
    def __init__ (self, name, color, game = None):
        self.__id = str(uuid.uuid4())
        self.__name = name
        self.__color = color
        self.__game = game

    @property
    def id (self):
        return self.__id

    @property
    def name (self):
        return self.__name

    @property
    def color (self):
        return self.__color

    @property
    def game (self):
        return self.__game
