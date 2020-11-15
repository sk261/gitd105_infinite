import copy

class Entity:
    def __init__(self):
        self.position = [0,0]
        self.type = ""
        self.blocking = False
        self.moving = False
        self.lastD = ""
    
    def clone(self):
        return copy.deepcopy(self)
        
class Player(Entity):
    def __init__(self):
        super(Player, self).__init__()
        self.type = "Player"
        self.moving = False
        self.health = 5
        self.inventory = []
        self.max_inventory = 3
        self.money = 0
        self.speed = 2
        self.blocking = True

    def addItem(self, entity):
        if self.max_inventory < len(self.inventory):
            self.inventory.append(entity)
        else:
            return False
        

class Monster(Entity):
    def __init__(self):
        super(Monster, self).__init__()
        self.type = "Monster"
        self.moving = True
        self.blocking = True
        self.health = 1
        self.damage = 1
        self.speed = 1
        self.target = None
        self.home = None
        self.path = []
        self.chasing = False
    
    def changeTarget(self, target):
        if not self.target == target:
            self.target = target
            self.path = []
    
    def requestSwap(self, requester_pos):
        if requester_pos in self.path:
            return True
        else:
            return False
    
    def updatePath(self):
        if self.target in self.path:
            while not (self.target == self.path.pop(0)):
                pass
        else:
            self.path = []
    

class Item(Entity):
    def __init__(self):
        super(Item, self).__init__()
        self.type = "Item"
    
DEFAULT_MONSTER = Monster()
DEFAULT_MONSTER.health = 5
DEFAULT_MONSTER.damage = 1
DEFAULT_MONSTER.speed = 1