class BonusGroup(object):
    def __init__ (self, name, value=1.0)
        self.__name = name
        self.__value = value
        self.__children = []

    def add_territory(self, territory):
        if territory not in self.__children:
            self.__children.append(territory)
            territory.registor_bonus_group(self)

    def remove_territory(self, territory):
        if territory in self.__children:
            self.__children.remove(territory)
            territory.unregister_bonus_group(self)

    @property
    def name (self):
        return self.__name

    @property
    def value (self):
        return self.__value

    @property
    def children (self):
        return self.__children.copy()
