from .moves import AttackMove, TransferMove, PlacementMove
import random

class Greedy(object):
    def generate_movelist(self, game, player):
        return []

class Horder(object):
    def generate_movelist(self, game, player):
        max_reinforcements = game.calculate_players_reinforcements(player)
        owned = game.get_player_territories(player)
        num_territories = len(owned)
        sample_of_owned = random.choices(list(owned),k=int(max_reinforcements))
        moves = [ PlacementMove(x,1,player) for x in sample_of_owned ]
        return moves
