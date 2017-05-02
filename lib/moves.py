ATTACK_KILL_PROB = 0.6
DEFEND_KILL_PROB = 0.7
class Move():
    def __init__ (self, to, amount, player):
        self.to = to
        self.amount = amount
        self.player = player
        self.validations = []

    def validate(self,game):
        for check in self.validations:
            issue = check(game)
            if issue:
                raise issue

class AttackMove(Move):
    def __init__ (self, _from, to, amount, player):
        super().__init__(to,amount,player)
        self._from = _from
        self.validations.append(self.check_ownership)
        self.validations.append(self.check_amount)

    # TODO CHECK ADJACENCY

    def check_ownership (self, game):
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)
        player = game.get_player(self.player)
        if from_territory.owner != player:
            msg = 'player does not own attacking territory ({},{})'
            return Exception(msg.format(player,from_territory))
        if to_territory.owner == player:
            msg = 'player owns territory it is attacking ({},{})'
            return Exception(msg.format(player,to_territory))

    def check_amount (self, game):
        from_territory = game.get_territory(self._from)
        if self.amount > from_territory.num_troops-1:
            msg = 'not enough troops ({},{})'
            return Exception(msg.format(self.amount,from_territory))

    def execute(self, game):
        self.validate(game)
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)

        from_territory.num_troops -= self.amount

        attacker_kills = round(self.amount*ATTACK_KILL_PROB)
        defend_kills = round(to_territory.num_troops*DEFEND_KILL_PROB)

        success = attacker_kills > to_territory.num_troops
        if success:
            move_troops = self.amount - defend_kills
            game.player_take_control_of(self.player,to_territory,move_troops)
        else:
            to_territory.num_troops -= attacker_kills
            if self.amount > defend_kills:
                from_territory.num_troops += self.amount - defend_kills

class TransferMove(Move):
    def __init__ (self, _from, to, amount, player):
        super().__init__(to,amount,player)
        self._from = _from
        self.validations.append(self.check_ownership)
        self.validations.append(self.check_amount)

    def check_ownership (self, game):
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)
        player = game.get_player(self.player)
        if from_territory.owner != player:
            msg = 'player does not own source ({},{})'
            return Exception(msg.format(player,from_territory))
        if to_territory.owner != player:
            msg = 'player does not own destination ({},{})'
            return Exception(msg.format(player,to_territory))

    def check_amount (self, game):
        from_territory = game.get_territory(self._from)
        if self.amount > from_territory.num_troops-1:
            msg = 'not enough troops ({},{})'
            return Exception(msg.format(self.amount,from_territory))

    def execute(self, game):
        self.validate(game)
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)
        from_territory.num_troops -= self.amount
        to_territory.num_troops += self.amount

class PlacementMove(Move):
    def __init__ (self, to, amount, player):
        super().__init__(to,amount,player)
        self.validations.append(self.check_ownership)
        self.validations.append(self.check_amount)

    def execute(self, game):
        self.validate(game)
        to_territory = game.get_territory(self.to)
        to_territory.num_troops += self.amount

    def check_ownership (self, game):
        to_territory = game.get_territory(self.to)
        player = game.get_player(self.player)
        if to_territory.owner != player:
            msg = 'player does not own destination ({},{})'
            return Exception(msg.format(player,to_territory))

    def check_amount (self, game):
        player = game.get_player(self.player)
        if self.amount > game.calculate_players_reinforcements(player):
            msg = 'not enough reinforcements ({})'
            return Exception(msg.format(self.amount))

