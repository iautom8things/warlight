from .player import Player
from .territory import Territory
import random
import networkx as nx
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

class Game(object):
    def __init__ (self,seed=None,starting_troops=10,adjmat=None,draw_graphs=False):
        random.seed(seed)
        self.__start_time = datetime.now()
        self.__players = {}
        self.__player_territories = {}
        self.__started = False
        self.__territories = {}
        self.__bonus_groups = {}
        self.__starting_troops = starting_troops
        self.__turn = 0
        self.__eliminated_players = set()
        self.adjmat = adjmat
        self.__G = nx.Graph()
        self.__draw_graphs = draw_graphs
        for k, data in adjmat.items():
            for n in data['adj_nodes']:
                self.__G.add_edge(k,n)
        self.__output_dir = 'fig/{}'.format(self.__start_time)
        if not os.path.isdir(self.__output_dir):
            os.mkdir(self.__output_dir)


    def __draw_map (self):
        if not self.draw_graphs:
            return

        graph_pos = nx.spectral_layout(self.__G)
        neutral = [ x.name for x in self.get_neutral_territories() ]
        nx.draw_networkx_nodes(self.__G,graph_pos, node_size=1, node_color='grey', alpha=0.3,nodelist=neutral)
        for p, player in self.players.items():
            nodes = [ (x.name,x.num_troops) for x in self.get_player_territories(player)]
            names = [ x[0] for x in nodes ]
            sizes = [ x[1] for x in nodes ]
            nx.draw_networkx_nodes(self.__G,graph_pos, node_size=sizes, node_color=player.color, alpha=0.5,nodelist=names)
        nx.draw_networkx_edges(self.__G,graph_pos, alpha=0.1)
        if self.is_done():
            name = 'game_over'
        else:
            name = 'turn_{}'.format(self.__turn)

        fname = '{}.png'.format(name)
        output = os.path.join(self.__output_dir,fname)
        plt.savefig(output,dpi=450)
        plt.clf()

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

    def run_game (self):
        results = []
        while not self.is_done():
            self.__draw_map()
            result = self.process_turn()
            results.append(result)
        self.__draw_map()
        output = os.path.join(self.__output_dir,'movelist')
        with open(output,'w') as f:
            f.write("\n".join([ json.dumps(x) for x in results ]))

        for key in ['num_troops','num_territories','income']:
            plt.clf()
            for pid, player in self.players.items():
                points = [ x['players'][player.name][key] for x in results ]
                plt.plot(range(len(points)),points,color=player.color)

            fname = '{}.png'.format(key)
            output = os.path.join(self.__output_dir,fname)
            plt.savefig(output,dpi=450)
            plt.clf()

        return results

    def process_turn (self):
        if self.is_done():
            print("Game has finished!  {} won!".format(self.__winner))
            return

        turn_results = { 'turn': self.turn, 'players':{},'placements':[],'moves':[]}
        for p, player in self.players.items():
            num_reinforcements = self.calculate_players_reinforcements(player)
            num_troops = self.count_troops(player)
            num_territories = len(self.player_territories[p])
            turn_results['players'][player.name] = {'income':num_reinforcements,'num_troops':num_troops,'num_territories':num_territories}

        # for each player, let them generate a move list
        move_lists = { pid : player.generate_movelist(self) for pid, player in self.players.items() }

        for pid, movelist in move_lists.items():
            for placement in movelist['placements']:
                move_result = self.make_move(pid,placement)
                turn_results['placements'].append(move_result)

        moves_left = True
        while moves_left:
            moves_left = False
            players = list(move_lists.keys())
            random.shuffle(players)
            for pid in players:
                if not move_lists[pid]['moves']:
                    continue
                move = move_lists[pid]['moves'].pop(0)
                move_result = self.make_move(pid,move)
                turn_results['moves'].append(move_result)
                moves_left |= len(move_lists[pid]['moves']) > 0

        self.__turn += 1
        return turn_results

    def make_move (self, pid, move):
        result = move.execute(self)
        return result

    def count_troops (self, player):
        player = self.get_player(player)
        troop_count = 0
        for territory in self.player_territories[player.id]:
            troop_count += territory.num_troops
        return troop_count

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
                self.__player_territories[pid].remove(territory)

        if new_troop_amount is not None:
            territory.num_troops = new_troop_amount

    def get_player_territories (self, player):
        player = self.get_player(player)
        return self.player_territories[player.id]

    def get_neutral_territories (self):
        neutral = { territory for name, territory in self.territories.items() if territory.owner is None }
        return neutral

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

    @property
    def draw_graphs (self):
        return self.__draw_graphs

    @draw_graphs.setter
    def draw_graphs (self,val):
        self.__draw_graphs = val

