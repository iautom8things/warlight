from .player import Player

class Territory(object):
    def __init__ (self, name):
        self.__name = name
        self.__neighboors = set()
        self.__num_troops = 0
        self.__owner = None
        self.__bonus_groups = set()

    def register_bonus_group (self, bonus_group):
        if bonus_group not in self.__bonus_groups:
            self.__bonus_groups.add(bonus_group)

    def unregister_bonus_group (self, bonus_group):
        if bonus_group in self.__bonus_groups:
            self.__bonus_groups.remove(bonus_group)

    def add_neighboor (self, territory):
        if territory not in self.__neighboors:
            self.__neighboors.add(territory)

    def remove_neighboor(self, territory):
        if territory in self.__neighboors:
            self.__neighboors.remove(territory)

    @property
    def name (self):
        return self.__name

    @property
    def neighboors (self):
        return self.__neighboors.copy()

    @property
    def num_troops (self):
        return self.__num_troops

    @property
    def owner (self):
        return self.__owner

    @property
    def bonus_groups (self):
        return self.__bonus_groups.copy()

    @owner.setter
    def owner (self, player):
        if type(player) != Player:
            raise Exception('owner must be Player object ({} given)'.format(player))
        self.__owner = player

    @num_troops.setter
    def num_troops (self, value):
        if type(value) != int:
            raise Exception('owner must be int ({} given)'.format(value))
        self.__num_troops = value

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        adj_str = ",".join([ x.name for x in self.__neighboors])
        if len(adj_str) >= 15:
            adj_str = "{}...".format(adj_str[:15])
        bg_str = ",".join([ x.name for x in self.__bonus_groups])
        if len(bg_str) >= 15:
            bg_str = "{}...".format(bg_str[:15])
        return "<Node: {} Troops: {} Adj: [{}] Bonus Groups: [{}]>".format(self.__name,self.__num_troops,adj_str,bg_str)
