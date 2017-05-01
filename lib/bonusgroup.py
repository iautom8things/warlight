class BonusGroup(object):
    def __init__ (self, name, value=1.0):
        self.__name = name
        self.__value = value
        self.__children = set()

    def add_territory(self, territory):
        if territory not in self.__children:
            self.__children.add(territory)
            territory.register_bonus_group(self)

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

    def __repr__ (self):
        return str(self)

    def __str__ (self):
        node_str = ",".join([ x.name for x in self.__children])
        if len(node_str) >= 15:
            node_str = "{}...".format(node_str[:15])
        return "<Group: {} Value: {} Nodes: [{}]>".format(self.__name,self.__value,node_str)
