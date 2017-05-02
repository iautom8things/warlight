import uuid
from .moves import AttackMove, TransferMove, PlacementMove
from .strategy import *

class Player(object):
    def __init__ (self, name, color):
        self.__id = str(uuid.uuid4())
        self.__name = name
        self.__color = color
        self.__strategy = Horder()

    def generate_movelist (self,game):
        return self.__strategy.generate_movelist(game,self)

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
    def strategy (self):
        return self.__strategy

    @strategy.setter
    def strategy (self, strategy):
        self.__strategy = strategy

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        return "<Player: {} id: {} color: {}>".format(self.__name,self.__id, self.__color)
