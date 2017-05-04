from .moves import AttackMove, TransferMove, PlacementMove
import random

class Strategy(object):
    def __repr__ (self):
        return str(self)

    def __str__ (self):
        return self.__class__.__name__

class Greedy(Strategy):
    def generate_movelist(self, game, player):
        reinforcements = game.calculate_players_reinforcements(player)
        border = game.get_border_territories(player)
        attackable = game.get_attackable_territories(player)
        scores = [ (x,game.adjmat[x.name]['value']) for x in attackable ]

        scores.sort(key=lambda x: x[1],reverse=True)
        target, score = scores[0]

        attack_source = list(target.neighbors.intersection(border))[0]
        attack_force = reinforcements + attack_source.num_troops - 1

        moves = { 'placements': [ PlacementMove(attack_source,reinforcements,player) ],
                   'moves': [ AttackMove(attack_source,target,attack_force,player) ] }
        return moves

class Opportunistic(Strategy):
    def generate_movelist(self, game, player):
        reinforcements = game.calculate_players_reinforcements(player)
        border = game.get_border_territories(player)
        attackable = game.get_attackable_territories(player)
        attackable_by_troops = [ x for x in attackable ]

        attackable_by_troops.sort(key=lambda x: x.num_troops)
        placements = []
        attacks = []
        for t in attackable_by_troops:
            if reinforcements < 1:
                break
            sources = list(border.intersection(t.neighbors))
            sources.sort(key=lambda x: x.num_troops,reverse=True)
            source = sources[0]
            needs = 0
            if source.num_troops < t.num_troops*2:
                needs = t.num_troops*2-(source.num_troops-1)
                if needs > reinforcements:
                    needs = reinforcements
                placements.append(PlacementMove(source,needs,player))
                reinforcements -= needs
            attack_with = source.num_troops+needs-1
            if attack_with > 0:
                attacks.append(AttackMove(source,t,attack_with,player))

        if reinforcements > 0:
            sample_of_border = random.choices(list(border),k=int(reinforcements))
            new_placements = [ PlacementMove(x,1,player) for x in sample_of_border ]
            placements += new_placements

        moves = { 'placements': placements, 'moves': attacks }
        return moves

class Horder(Strategy):
    def generate_movelist(self, game, player):
        max_reinforcements = game.calculate_players_reinforcements(player)
        owned = game.get_player_territories(player)
        sample_of_owned = random.choices(list(owned),k=int(max_reinforcements))
        moves = { 'placements': [ PlacementMove(x,1,player) for x in sample_of_owned ],
                  'moves': [] }
        return moves
