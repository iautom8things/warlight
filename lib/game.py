from .player import Player
from .territory import Territory
import random
class Game(object):
    def __init__ (self,seed=None,starting_troops=10):
        random.seed(seed)
        player_1 = Player('Player 1','blue',self)
        player_2 = Player('Player 2','red',self)
        self.__players = { player_1.id : player_1, player_2.id : player_2 }
        self.__player_territories = { player_1.id : set(), player_2.id : set() }
        self.__started = False
        self.__territories = {}
        self.__bonus_groups = {}
        self.__starting_troops = starting_troops

    def is_done (self):
        if not self.__started:
            return False

        result = False
        for p, ts in self.__player_territories.items():
            if len(ts) == 0:
                result = True
        return result

    def winner (self):
        if not self.__started:
            return None

        still_playing = []
        for p, ts in self.__player_territories.items():
            if len(ts) > 0:
                still_playing.append(p)

        winner = None
        if len(still_playing) == 1:
            winner = still_playing[0]
        return winner

    def process_turn (self):
        self.__started = True

    def add_territory (self, territory):
        if territory.name not in self.__territories:
            self.__territories[territory.name] = territory

    def remove_territory (self, territory):
        if territory.name in self.__territories:
            del self.__territories[territory.name]

    def add_bonus_group (self, bonus_group):
        if bonus_group.name not in self.__bonus_groups:
            self.__bonus_groups[bonus_group.name] = bonus_group

    def remove_bonus_group (self, bonus_group):
        if bonus_group.name in self.__bonus_groups:
            del self.__bonus_groups[bonus_group.name]

    @property
    def territories (self):
        return self.__territories.copy()

    @property
    def bonus_groups (self):
        return self.__bonus_groups.copy()

    @property
    def players (self):
        return self.__players.copy()

    @property
    def player_territories (self):
        return self.__player_territories.copy()

    @property
    def starting_troops (self):
        return self.__starting_troops
