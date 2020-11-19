import copy

class Entity:
    def __init__(self):
        self.position = [0,0]
        self.type = ""
        self.blocking = False
        self.moving = False
        self.lastD = ""
        self.health = 0
    
    def clone(self):
        return copy.deepcopy(self)
        
class Player(Entity):
    def __init__(self):
        super(Player, self).__init__()
        self.type = "Player"
        self.moving = False
        self.health = 6
        self.max_health = 6
        self.armor = 5
        self.armor_quality = 3
        self.armor_max_quality = 5
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
    def __init__(self, index):
        super(Item, self).__init__()
        self.type = "Item"
        self.index = index
        self.quality = 0

class Decor(Entity): #Blood
    def __init__(self, index):
        super(Decor, self).__init__()
        self.type = "Decor"
        self.index = index


class Trap(Entity):
    def __init__(self, trap):
        super(Trap, self).__init__()
        self.type = "Trap"
        self.trap = trap
        self.damage = TRAPS[trap][2]
        self.current = TRAPS[trap][0]
        self.post_image = TRAPS[trap][1]
        self.requires_dialogue = TRAPS[trap][3]
        self.sprung = False
    
    def Spring(self, entity):
        entity.health -= damage
        self.current = self.post_Image
        if self.trap == "Spikes":
            self.post_image = None
            self.damage = 0
        return False



# [First image id], [Second image id], [Damage dealt], [Dialogue]
TRAPS = {
    "Spikes":   [ [6, 5],   [6, 6], 1,  False],
    "Hole":     [ [4, 1],   None,   0,  True],
    "Portal":   [ [4, 2],   None,   0,  True]
}
DEFAULT_MONSTER = Monster()
DEFAULT_MONSTER.health = 5
DEFAULT_MONSTER.damage = 1
DEFAULT_MONSTER.speed = 1