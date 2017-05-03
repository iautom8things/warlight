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
        self.validations.append(self.check_adjacency)

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

    def check_adjacency (self, game):
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)
        if to_territory not in from_territory.neighbors:
            msg = 'territory must be adjacent to attack {} -> {}'
            return Exception(msg.format(from_territory,to_territory))

    def check_amount (self, game):
        from_territory = game.get_territory(self._from)
        if self.amount > from_territory.num_troops-1:
            msg = 'not enough troops ({},{})'
            return Exception(msg.format(self.amount,from_territory))

    def execute(self, game):
        player = game.get_player(self.player)
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)

        self.validate(game)

        from_territory.num_troops -= self.amount
        num_attacking = self.amount
        num_defending = to_territory.num_troops

        attacker_kill_potential = round(num_attacking*ATTACK_KILL_PROB)
        defender_kill_potential = round(num_defending*DEFEND_KILL_PROB)

        attacker_kills = min(attacker_kill_potential,to_territory.num_troops)
        defender_kills = min(defender_kill_potential,num_attacking)

        success = attacker_kill_potential > to_territory.num_troops
        if success:
            move_troops = self.amount - defender_kills
            game.player_take_control_of(self.player,to_territory,move_troops)
        else:
            to_territory.num_troops -= attacker_kills
            if self.amount > defender_kills:
                from_territory.num_troops += self.amount - defender_kills

        result = {
                    'player': player.name,
                    'type': 'attack',
                    'from': from_territory.name,
                    'to': to_territory.name,
                    'defending_player': to_territory.owner.name or 'no one',
                    'attacking': num_attacking,
                    'defending': num_defending,
                    'attacker_kills': attacker_kills,
                    'defender_kills': defender_kills,
                    'success': success
                }
        return result

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        return "<AttackMove: From: {} To: {} #: {} By: {}>".format(self._from,self.to,self.amount,self.player)

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
        player = game.get_player(self.player)
        from_territory = game.get_territory(self._from)
        to_territory = game.get_territory(self.to)

        self.validate(game)

        from_starting = from_territory.num_troops
        to_starting = to_territory.num_troops

        from_territory.num_troops -= self.amount
        to_territory.num_troops += self.amount

        result = {
                    'player': player.name,
                    'type': 'transfer',
                    'from': from_territory.name,
                    'to': to_territory.name,
                    'amount': self.amount,
                    'from_starting': from_starting,
                    'to_starting': to_starting,
                    'from_ending': from_territory.num_troops,
                    'to_ending': to_territory.num_troops,
                }
        return result

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        return "<TransferMove: From: {} To: {} #: {} By: {}>".format(self._from.name,self.to.name,self.amount,self.player)

class PlacementMove(Move):
    def __init__ (self, to, amount, player):
        super().__init__(to,amount,player)
        self.validations.append(self.check_ownership)
        self.validations.append(self.check_amount)

    def execute(self, game):
        player = game.get_player(self.player)
        to_territory = game.get_territory(self.to)

        self.validate(game)

        to_starting = to_territory.num_troops
        to_territory.num_troops += self.amount

        result = {
                    'player': player.name,
                    'type': 'placement',
                    'to': to_territory.name,
                    'amount': self.amount,
                    'to_starting': to_starting,
                    'to_ending': to_territory.num_troops,
                }
        return result

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

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        return "<PlacementMove: To: {} #: {} By: {}>".format(self.to,self.amount,self.player)
