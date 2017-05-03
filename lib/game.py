from .player import Player
from .territory import Territory
import random

class Game(object):
    def __init__ (self,seed=None,starting_troops=10,adjmat=None):
        random.seed(seed)
        self.__players = {}
        self.__player_territories = {}
        self.__started = False
        self.__territories = {}
        self.__bonus_groups = {}
        self.__starting_troops = starting_troops
        self.__turn = 0
        self.__eliminated_players = set()
        self.adjmat = adjmat

    def add_player (self, new_player):
        if self.__started:
            raise Exception('players cannot be added after game has started')
        if type(new_player) != Player:
            raise Exception('must provide Player object')
        self.__players[new_player.id] = new_player
        self.__player_territories[new_player.id] = set()

    def is_done (self):
        if not self.__started:
            return False

        still_playing = []
        for p, ts in self.__player_territories.items():
            if len(ts) == 0:
                self.__eliminated_players.add(p)
            else:
                still_playing.append(p)

        game_over = len(self.__eliminated_players) == len(self.__players)-1
        if game_over:
            self.__winner = self.__players[still_playing[0]]

        return game_over

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
        self.__turn += 1

    def player_controlled_bonus_groups (self, player):
        player = self.get_player(player)
        owned_territories = self.__player_territories[player.id]
        return { bg for bg_name, bg in self.bonus_groups.items() if owned_territories.issuperset(bg.children) }

    def calculate_players_reinforcements (self, player):
        reinforcements = self.starting_troops
        player = self.get_player(player)

        owned_territories = self.__player_territories[player.id]
        for bg in self.player_controlled_bonus_groups(player):
            if owned_territories.issuperset(bg.children):
                reinforcements += bg.value
        return int(reinforcements)

    def process_turn (self):
        if self.is_done():
            print("Game has finished!  {} won!".format(self.__winner))
            return

        print("## Turn {}".format(self.turn))
        for p, player in self.players.items():
            print ("  {} gets {} troops".format(player.name,self.calculate_players_reinforcements(player)))
        # for each player, let them generate a move list
        move_lists = { pid : player.generate_movelist(self) for pid, player in self.players.items() }

        print("--> Deployment phase")
        for pid, movelist in move_lists.items():
            for placement in movelist['placements']:
                self.make_move(pid,placement)

        print("--> Move phase")
        moves_left = True
        while moves_left:
            moves_left = False
            players = list(move_lists.keys())
            random.shuffle(players)
            for pid in players:
                if not move_lists[pid]['moves']:
                    continue
                move = move_lists[pid]['moves'].pop(0)
                self.make_move(pid,move)
                moves_left |= len(move_lists[pid]['moves']) > 0

        self.__turn += 1

    def make_move (self, pid, move):
        move.execute(self)

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
        player = self.get_player(player)
        territory = self.get_territory(territory)

        # set owner
        territory.owner = player
        self.__player_territories[player.id].add(territory)
        # ensure territory is not owned by other players
        for pid, territories in self.__player_territories.items():
            if territory in territories and pid != player.id:
                territories.remove(territory)

        if new_troop_amount is not None:
            territory.num_troops = new_troop_amount

    def get_player_territories (self, player):
        player = self.get_player(player)
        return self.player_territories[player.id]

    def get_attackable_territories (self, player):
        owned = self.get_player_territories(player)
        all_neighbors = set()
        for owned_t in owned:
            all_neighbors = all_neighbors.union(owned_t.neighbors)

        return all_neighbors - owned

    def get_border_territories (self, player):
        owned = self.get_player_territories(player)
        border = set()
        for owned_t in owned:
            if owned_t.neighbors - owned:
                border.add(owned_t)

        return border

    def get_player (self, player):
        if player in self.players:
            player = self.__players[player]
        elif type(player) != Player:
            raise Exception("player must be either of type Player or a player_id")

        return player

    def get_territory (self, territory):
        if territory in self.territories:
            territory = self.__territories[territory]
        elif type(territory) != Territory:
            raise Exception("territory must be either of type Territory or a territory name")

        return territory

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

    @property
    def turn (self):
        return self.__turn

