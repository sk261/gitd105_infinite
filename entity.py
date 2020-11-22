import copy

class Entity:
    def __init__(self):
        self.position = [0,0]
        self.type = ""
        self.blocking = False
        self.moving = False
        self.lastD = ""
        self.health = 0
        self.hit = False
    
    def clone(self):
        return copy.deepcopy(self)
    
        
class Player(Entity):
    def __init__(self):
        super(Player, self).__init__()
        self.type = "Player"
        self.moving = False
        self.health = 6
        self.max_health = 6
        self.armor = None
        self.armor_quality = 0
        self.armor_max_quality = 0
        self.max_inventory = 3
        self.inventory = [None]*self.max_inventory
        self.inventory[0] = Item(0)
        self.inventory[1] = Item(7)
        self.inventory[2] = Item(8)
        self.money = 0
        self.speed = 2
        self.blocking = True

    def dealDamage(self, damage):
        damage_dealt = max(damage - self.armor_quality, 0)
        self.health = max(self.health - damage_dealt, 0)
        if self.armor != None:
            self.armor_quality -= damage
            if self.armor_quality <= 0:
                self.armor = None
                self.armor_quality = 0
        return damage_dealt
        
        

class Monster(Entity):
    def __init__(self):
        super(Monster, self).__init__()
        self.type = "Monster"
        self.moving = True
        self.blocking = True
        self.health = 1
        self.damage = 1
        self.speed = 2
        self.moves = 0
        self.vision = 4
        self.target = None
        self.avoided_paths = []
        self.path = []
        self.chasing = False
        self.stunned = 0
        self.home = None
    
    def avoided(self):
        return self.avoided_paths

    def avoid(self, path):
        self.avoided_paths.append(path)
    
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
            
    def dealDamage(self, damage):
        pass
    

class Item(Entity):
    def __init__(self, index):
        super(Item, self).__init__()
        self.type = "Item"
        self.index = index
        self.quality = 0

class Decor(Entity): #Blood
    def __init__(self, index, pos, category = 4):
        super(Decor, self).__init__()
        self.type = "Decor"
        self.category = category
        self.index = index
        self.position = [el for el in pos]


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
DEFAULT_MONSTER.damage = 3
DEFAULT_MONSTER.speed = 2