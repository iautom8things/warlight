from .moves import AttackMove, TransferMove, PlacementMove
import random

class Greedy(object):
    def generate_movelist(self, game, player):
        reinforcements = game.calculate_players_reinforcements(player)
        owned = game.get_player_territories(player)
        border = game.get_border_territories(player)
        attackable = game.get_attackable_territories(player)
        scores = [ (x,game.adjmat[x.name]['value']) for x in attackable ]

        scores.sort(key=lambda x: x[1],reverse=True)
        target, score = scores[0]

        attack_source = list(target.neighbors.intersection(owned))[0]
        attack_force = reinforcements + attack_source.num_troops - 1

        # what if 

        moves = { 'placements': [ PlacementMove(attack_source,reinforcements,player) ],
                   'moves': [ AttackMove(attack_source,target,attack_force,player) ] }
        return moves

class Horder(object):
    def generate_movelist(self, game, player):
        max_reinforcements = game.calculate_players_reinforcements(player)
        owned = game.get_player_territories(player)
        num_territories = len(owned)
        sample_of_owned = random.choices(list(owned),k=int(max_reinforcements))
        moves = { 'placements': [ PlacementMove(x,1,player) for x in sample_of_owned ],
                  'moves': [] }
        return moves
