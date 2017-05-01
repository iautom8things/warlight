from .player import Player
from .territory import Territory
import random
class Game(object):
    def __init__ (self,seed=None,starting_troops=10):
        random.seed(seed)
        player_1 = Player('Player 1','blue')
        player_2 = Player('Player 2','red')
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

    def start_game (self, num_init_territories):
        if self.__started:
            raise Exception("game already started")
        num_starting = len(self.__players) * num_init_territories
        if num_starting > len(self.__territories):
            raise Exception("num_init_territories too large")
        t_names = list(self.__territories.keys())
        random.shuffle(t_names)
        start, end = 0, num_init_territories
        for pid in self.__player_territories:
            curr_territories = t_names[start:end]
            for tname in curr_territories:
                self.player_take_control_of(pid,tname,self.starting_troops)
            start, end = end, end+num_init_territories

        self.__started = True

    def process_turn (self):
        pass

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

    def player_take_control_of (self, player, territory, new_troop_amount = None):
        if player in self.players:
            player = self.get_player(player)
        elif type(player) != Player:
            raise Exception("player must be either of type Player or a player_id")

        if territory in self.territories:
            territory = self.get_territory(territory)
        elif type(territory) != Territory:
            raise Exception("territory must be either of type Territory or a territory name")

        # set owner
        territory.owner = player
        self.__player_territories[player.id].add(territory)
        # ensure territory is not owned by other players
        for pid, territories in self.__player_territories.items():
            if territory in territories and pid != player.id:
                territories.remove(territory)

        if new_troop_amount is not None:
            territory.num_troops = new_troop_amount

    def get_player (self, player_id):
        if player_id in self.players:
            return self.__players[player_id]
        else:
            raise Exception('player not found')

    def get_territory (self, territory):
        if territory in self.territories:
            return self.__territories[territory]
        else:
            raise Exception('territory not found')

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
