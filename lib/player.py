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

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        return "<Player: {} id: {} color: {}>".format(self.__name,self.__id, self.__color)
