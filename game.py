import map
import pygame
import entity as E
import math
import random
random.seed()
import time as _time
time = lambda: int(round(_time.time() * 1000))


class Game:
    def __init__(self, spritesheet):
        self.player = E.Player()
        self.direction = ""
        self.player_moves = 0

        self.level = 0
        self.newMap(30)

        self.sprites = spritesheet

        self.currentTriggers = []
        self.graphics_updates = True
        self.bg_image = None
        self.fg_image = None
        self.gg_image = None
        self.last_image = None
        self.Cooldown = 0
        self.maxCooldown = 200
        self.waitForDialogue = False
        self.graphicsCD = 0
        self.currentTrap = None
        self.arrow = None
        self.hiding = False
        self.bouncing = False
        self.bouncingCD = 0

        self.currentCellContents = []
        self.DEBUGGING = False
    
    def newMap(self, x):
        self.level += 1
        self.map = map.Map()
        self.map.generateMap(int(x/self.map.size[0]))
        self.map.prepare_landing(x)
        self.player.position = [x,1]
        self.map.addEntity(self.player)
        self.map.generateMonsters(10 + 2*self.level, E.DEFAULT_MONSTER)
        self.map.revealCellsFromEntity(self.player)
        for entity in self.map.contents:
            if entity.type == "Monster":
                entity.chasing = False
    
    def triggerInput(self, triggers):
        if len(triggers) == 0: return
        for n in triggers.keys():
            if n in self.currentTriggers and not triggers[n]:
                self.currentTriggers.remove(n)
            elif triggers[n] and not (n in self.currentTriggers):
                self.currentTriggers.append(n)
    
    def handleControls(self):
        keys = self.currentTriggers
        
        if 'up' in keys:
            self.direction = "N"
        if 'down' in keys:
            self.direction = "S"
        if 'right' in keys:
            self.direction = "E"
        if 'left' in keys:
            self.direction = "W"
        if 'space' in keys:
            self.direction = False
            #self.DEBUGGING = not self.DEBUGGING
            #self.map.DEBUGGING = not self.map.DEBUGGING
            pass
       
        if len([el for el in ['1','2','3'] if el in keys]) > 0:
            index = 0
            for n in range(3):
                if ['1', '2', '3'][n] in keys:
                    index = n
                    break
                
            item_list = []
            trap_list = []
            for content in self.currentCellContents:
                if content.type == "Trap":
                    trap_list.append(content)
                elif content.type == "Item":
                    item_list.append(content)
            # Item key selected
            # 1, 2, and 3 do different things depending on situation.
            if len(trap_list) > 0 and trap_list[0].trap == "Hole":
                if index == 0:
                    self.direction = False
                    self.hiding = True
                    for entity in self.map.contents:
                        if entity.type == "Monster":
                            entity.changeTarget(entity.home)
                    pass
                elif index == 1:
                    self.hiding = False
                    self.waitForDialogue = False
                    pass
            elif len(item_list) > 0: # PIck up item
                self.map.removeEntity(item_list[0])
                self.player.inventory[index] = item_list[0]
                self.graphics_updates = True
            else:
                if not self.player.inventory[index] is None:
                    item = self.player.inventory[index]
                    if item.index == 0:
                        # Item book
                        self.map.revealCellsInRadius(self.player.position, 15)
                        # Reveals everything 10 tiles around you.
                    elif item.index == 1:
                        # Item potion
                        self.player.health = min(self.player.health + 2, self.player.max_health)
                        # Heals player
                    elif item.index == 5:
                        # Item leather armor
                        self.player.armor = 5
                        self.player.armor_quality = 3
                        self.player.armor_max_quality = 3
                        # Equip new armor
                        pass
                    elif item.index == 6:
                        # Item metal armor
                        self.player.armor = 6
                        self.player.armor_quality = 5
                        self.player.armor_max_quality = 5
                        # Equip new armor
                        pass
                    elif item.index == 7:
                        # Item shield
                        self.map.cells[self.player.position[0]][self.player.position[1]].walltype = 7
                        self.map.cells[self.player.position[0]][self.player.position[1]].wall = True
                        # Place a wall on the player's space
                        pass
                    elif item.index == 8:
                        self.arrow = E.Projectile(self.player.position, self.player.lastD)
                        self.waitForDialogue = True
                        # Attack down a hall (knocks out someone for 2 turns)
                        pass
                    elif item.index == 9:
                        # Item orb
                        for entity in self.map.contents:
                            if entity.type == "Monster":
                                entity.stunned += 1
                        # Knocks out everyone for 1 turn
                        pass
                    elif item.index == 10:
                        while self.map.moveEntity(self.player, self.player.lastD):
                            self.map.revealCellsFromEntity(self.player)
                        # You 'run' to the end of the hall.
                    elif item.index == 11:
                        for entity in self.map.contents:
                            if entity.type == "Monster" and math.dist(entity.position, self.player.position) <= 2:
                                for d in self.map.DX.keys():
                                    pos = [self.map.DX[d] + self.player.position[0], self.map.DY[d] + self.player.position[1]]
                                    if pos == entity.position:
                                        entity.stunned = 3
                                        break
                        # Stuns everyone adjacent to you for 3 turns.
                        pass
                    self.graphics_updates = True
                    self.player.inventory[index] = None
        self.currentTriggers = []
            

    
    def tick(self):
        self.size = pygame.display.get_surface().get_size()

        #TODO Have characters bounce and move
        if time() > self.graphicsCD:
            self.graphics_updates = True
            self.graphicsCD = time() + self.maxCooldown

        # Turn only triggers when player performs an action
        if time() < self.Cooldown:
            return False

        playerTurn = False
        if self.waitForDialogue:
            self.Cooldown = time() + self.maxCooldown
            self.graphics_updates = True
            if not self.currentTrap is None:
                self.Cooldown = time() + 4*self.maxCooldown
                sprung = self.currentTrap.Spring(self.player, self.map)
                if not sprung:
                    self.map.removeEntity(self.currentTrap)
                    self.currentTrap = None
                    self.waitForDialogue = False
            elif not self.arrow is None:
                if not self.map.moveEntity(self.arrow, self.arrow.dir):
                    _x = self.map.DX[self.arrow.dir] + self.arrow.position[0]
                    _y = self.map.DY[self.arrow.dir] + self.arrow.position[1]
                    blocker = self.map.cellHasType([_x, _y], "Monster")
                    if not blocker is False:
                        blocker.stunned += 2
                        self.map.addEntity(E.Decor(4, blocker.position))
                    self.map.removeEntity(self.arrow)
                    self.arrow = None
                    self.waitForDialogue = False





        self.handleControls()
        if self.direction == False:
            self.player_moves += 1
            self.graphics_updates = True
        elif self.direction != "" and not self.waitForDialogue:
            self.graphics_updates = True
            
            # Player movement
            if self.map.moveEntity(self.player, self.direction):
                if self.map.cells[self.player.position[0]][self.player.position[1]].exit:
                    self.newMap(self.player.position[0])
                    self.direction = ""
                    self.player_moves = 0
                    return True
                self.player.lastD = self.direction
                self.map.clearVisibility()
                self.map.revealCellsFromEntity(self.player)
                self.currentCellContents = self.map.cells[self.player.position[0]][self.player.position[1]].contents
                self.player_moves += 1
                self.graphics_updates = True
                # Check for traps
                for entity in self.currentCellContents:
                    if entity.type == "Trap":
                        self.waitForDialogue = entity.requires_dialogue
                        self.currentTrap = entity
                        if self.waitForDialogue:
                            self.Cooldown = time() + 4*self.maxCooldown
                            pass
                # Player moved successfully, entity target check for player
                for entity in self.map.contents:
                    if not entity.moving:
                        continue
                    if not self.hiding and self.map.entitySeesEntity(entity, self.player, "", entity.vision):
                        entity.changeTarget([self.player.position[0], self.player.position[1]])
                        entity.chasing = True

        if self.graphics_updates:
            for entity in self.map.contents:
                entity.hit = False

        if self.player_moves >= self.player.speed:
            playerTurn = True
        
        self.direction = ""
            

                

        if playerTurn:
            self.Cooldown = time() + self.maxCooldown
            arr = self.map.contents
            acted = False
            for entity in arr:
                if not entity.moving:
                    continue
                if entity.stunned > 0:
                    entity.moves = 0
                    entity.stunned -= 1
                    entity.chasing = False
                    continue
                if entity.moves <= 0:
                    continue
                if not self.hiding and self.map.entitySeesEntity(entity, self.player, "", entity.vision):
                    entity.changeTarget([self.player.position[0], self.player.position[1]])
                    entity.chasing = True
                elif not entity.chasing or entity.position == entity.target:
                    entity.changeTarget(entity.home)
                    entity.chasing = False

                if len(entity.path) == 0:
                    entity.path = self.map.pathToPoint(entity.position, entity.target, 30)
                    if len(entity.path) == 0:
                        entity.home = [el for el in entity.position]

                    

                if len(entity.path) == 0 or entity.position == entity.target:
                    entity.path = []
                    continue
                dx, dy = 0, 0
                while dx == 0 and dy == 0 and len(entity.path) > 0:
                    loc = entity.path.pop(0)
                    dx = loc[0] - entity.position[0]
                    dy = loc[1] - entity.position[1]
                if dx < 0:
                    d = "W"
                elif dx > 0:
                    d = "E"
                elif dy > 0:
                    d = "N"
                elif dy < 0:
                    d = "S"
                if not self.map.moveEntity(entity, d):
                    # Bumped
                    blocker = self.map.cellHasType(loc, entity.type)
                    if not blocker == False:
                        if blocker.requestSwap(entity.position):
                            self.map.swapEntities(blocker, entity)
                            blocker.updatePath()
                            entity.updatePath()
                    else:
                        if self.player.position == loc:
                            if self.player.dealDamage(entity.damage) > 0:
                                self.map.addEntity(E.Decor(4, self.player.position))
                                entity.moves = 0
                                acted = True
                                entity.lastD = d
                                self.player.hit = True
                else:
                    entity.moves -= 1
                    acted = True
                    entity.lastD = d
            if not acted:
                for entity in arr:
                    if entity.moving:
                        entity.moves = entity.speed
                self.player_moves = 0
            else:
                self.graphics_updates = True

        if self.bouncingCD < time(): # Sure.
            self.bouncing = not self.bouncing
            self.bouncingCD = time() + self.maxCooldown
            self.graphics_updates = True
                            
                        

    def draw(self):
        if self.graphics_updates:
            self.graphics_updates = False
            self.bg_image = self.getBackgroundImage(self.player.position)
            self.fg_image = self.getForegroundImage(self.player.position)
            self.gg_image = self.getGUIImage()

        ret = pygame.Surface((self.size[0], self.size[1]))
        ret.blit(self.bg_image, (0, 0))
        ret.blit(self.fg_image, (0, 0))
        ret.blit(self.gg_image, (0, 0))
        
        return ret

    def getGUIImage(self):
        gg = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)
        gfinal = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)
        gi = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)
        gg.set_alpha(200)
        panelBG = self.sprites.getImage(1, 1)

        # Bottom panel prep
        revealed = False
        item_list = []
        trap_list = []
        for content in self.currentCellContents:
            if content.type == "Trap":
                if content.current is None:
                    continue
                revealed = True
                trap_list.append(content)
            elif content.type == "Item":
                revealed = True
                item_list.append(content.index) # Add item to the list

        # Left panel BG
        width = 5
        height = 10

        offset_y = self.size[1]/2 - height*self.sprites.cellSize[1]/2
        TL = (self.sprites.cellSize[0],(self.sprites.cellSize[1] + offset_y))
        w = width*self.sprites.cellSize[0]
        h = height*self.sprites.cellSize[1]
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                pos = (x*self.sprites.cellSize[0],(y*self.sprites.cellSize[1] + offset_y))
                gg.blit(panelBG, pos)
        
        # Left panel FG
        # Character
        cursor = TL[1] + self.sprites.cellSize[1]/2
        gi.blit(self.sprites.getImage(3, 0), (TL[0] + w/2 - self.sprites.cellSize[0]/2, TL[1] + self.sprites.cellSize[1]/2))
        # Hearts
        cursor += self.sprites.cellSize[1]
        full_hearts = int(self.player.health / 2)
        halfHeart = (self.player.health % 2 == 1)
        for _n in range(3):
            off = (_n-1) + 1/2
            n = 2-_n
            i = 4
            if n < full_hearts:
                i = 2
            elif n == full_hearts and halfHeart and self.player.health > 0:
                i = 3
            gi.blit(self.sprites.getImage(5, i), (TL[0] + w/2 - off*self.sprites.cellSize[0], cursor))
        # Current Armor
        cursor += self.sprites.cellSize[1]
        if not self.player.armor is None:
            gi.blit(self.sprites.getImage(5, self.player.armor), (TL[0] + w/2 - self.sprites.cellSize[0]/2, cursor))
            cursor += self.sprites.cellSize[1]
            pygame.draw.rect(
                gi,
                self.getPercentColour(self.player.armor_quality, self.player.armor_max_quality),
                pygame.Rect(TL[0] + w/2 - self.sprites.cellSize[0]/2, cursor, self.sprites.cellSize[0], 3))
        # Boxes
        cursor += 5
        for i in range(self.player.max_inventory):
            rgb = [(100, 100, 100), (150, 150, 150)]
            if len(item_list) > 0 and self.player.inventory[i] is None:
                rgb = [(70, 100, 70), (100, 150, 100)]
            elif len(item_list) > 0:
                rgb = [(100, 70, 70), (150, 100, 100)]
            pygame.draw.rect(
                gg,
                rgb[0],
                pygame.Rect(TL[0] + w/10, cursor, 8*w/10, self.sprites.cellSize[1]*1.5))
            pygame.draw.rect(
                gg,
                rgb[1],
                pygame.Rect(TL[0] + w/10 + 2, cursor + 2, 8*w/10 - 4, self.sprites.cellSize[1]*1.5 - 4))
            if len(item_list) > 0:
                # Draw arrow
                gi.blit(self.sprites.getImage(6, 7 + i), (TL[0] + 9*w/10, cursor))
            if not self.player.inventory[i] is None:
                item = self.player.inventory[i]
                gi.blit(self.sprites.getImage(5, item.index), (TL[0] + 2*w/10, cursor + self.sprites.cellSize[1]/2))
                dir_index = {"N":0.1, "E":0.2, "S":0.3, "W":0}
                _DX = {"N": 0, "S": 0, "E": self.sprites.cellSize[0], "W": 0}
                _DY = {"N": 0, "S": self.sprites.cellSize[1]/2, "E": self.sprites.cellSize[1]/2, "W":self.sprites.cellSize[1]/2}
                if item.index == 0: #Book
                    gi.blit(self.sprites.getImage(6, 0), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                elif item.index == 1: #potion
                    gi.blit(self.sprites.getImage(5, 2), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                elif item.index == 5: #leather armor
                    gi.blit(self.sprites.getImage(6, 3), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    gi.blit(self.sprites.getImage(6, 1), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                elif item.index == 6: #metal armor
                    gi.blit(self.sprites.getImage(6, 3), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    gi.blit(self.sprites.getImage(6, 2), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                elif item.index == 7: #shield
                    gi.blit(self.sprites.getImage(0, 0), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    gi.blit(self.sprites.getImage(6, 3), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                elif item.index == 8: #Bow
                    if self.player.lastD in _DX.keys():
                        _dir = dir_index[self.player.lastD]
                        # arrow
                        gi.blit(self.sprites.getImage(6, 10+_dir),
                        (TL[0] + 5*w/10 + _DX[self.map.OPPOSITE[self.player.lastD]], cursor + _DY[self.map.OPPOSITE[self.player.lastD]]))
                        # object
                        gi.blit(self.sprites.getImage(6, 1),
                        (TL[0] + 5*w/10 + _DX[self.player.lastD], cursor + _DY[self.player.lastD]))
                elif item.index == 9: #Orb
                    gi.blit(self.sprites.getImage(2, 0), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    gi.blit(self.sprites.getImage(6, 4), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    pass
                elif item.index == 10: #Boot
                    if self.player.lastD in _DX.keys():
                        _dir = dir_index[self.player.lastD]
                        # arrow
                        gi.blit(self.sprites.getImage(6, 10+_dir),
                        (TL[0] + 5*w/10 + _DX[self.map.OPPOSITE[self.player.lastD]], cursor + _DY[self.map.OPPOSITE[self.player.lastD]]))
                        # boot
                        gi.blit(self.sprites.getImage(6, 10+_dir), # ??? Maybe I should put a boot here.
                        (TL[0] + 5*w/10 + _DX[self.player.lastD], cursor + _DY[self.player.lastD]))
                    pass
                elif item.index == 11: #knife
                    # Surrounding? # EXTRA: make it apparent that it's surrounding the player
                    gi.blit(self.sprites.getImage(2, 0), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    gi.blit(self.sprites.getImage(6, 2), (TL[0] + 5*w/10, cursor + self.sprites.cellSize[1]/2))
                    pass
            cursor += 2*self.sprites.cellSize[1]


        if revealed:
            # Bottom panel BG
            width = 10
            height = 3

            offset_x = self.size[0]/2 - width*self.sprites.cellSize[1]/2
            offset_y = self.size[1] - ((3 + height)*self.sprites.cellSize[0]) 

            CENTER = (self.size[0]/2, self.size[1] - 3*self.sprites.cellSize[0])
            w = width*self.sprites.cellSize[0]
            h = height*self.sprites.cellSize[1]
            for x in range(1, width + 1):
                for y in range(1, height + 1):
                    pos = (x*self.sprites.cellSize[0] + offset_x,(y*self.sprites.cellSize[1] + offset_y))
                    gg.blit(panelBG, pos)
           
            cursor = 0
            if len(trap_list) > 0:
                n = 1
                if trap_list[0].trap == "Spikes":
                    n = 1
                elif trap_list[0].trap == "Hole":
                    n = 4
                elif trap_list[0].trap == "Portal":
                    n = 3
                w = (w -  n*self.sprites.cellSize[0]) /2
                pos = [w + cursor + offset_x + self.sprites.cellSize[0], (h + self.sprites.cellSize[1])/2 + offset_y] # First telement
                if trap_list[0].trap == "Spikes":
                    gi.blit(self.sprites.getImage(3, 0), pos) # Player
                    if trap_list[0].current[1] == 6:
                        gi.blit(self.sprites.getImage(6, 2), pos)
                    gi.blit(self.sprites.getImage(6, trap_list[0].current[1]), pos)
                elif trap_list[0].trap == "Hole":
                    # Goon w/Z  downArrow   overArrow   Goon w/!
                    # <1   Hole        Hole        <2
                    # Upper level
                    gi.blit(self.sprites.getImage(6, 10.3), pos) # Arrow down
                    gi.blit(self.sprites.getImage(4, 1), [pos[0], pos[1] + self.sprites.cellSize[1]]) # hole
                    # 2
                    pos[0] += self.sprites.cellSize[0]
                    gi.blit(self.sprites.getImage(2, 0), pos) # Goon
                    gi.blit(self.sprites.getImage(6, 4), pos) # Z
                    # Selection arrow 1
                    gi.blit(self.sprites.getImage(6, 7), [pos[0], pos[1] + self.sprites.cellSize[1]])
                    # 3
                    pos[0] += self.sprites.cellSize[0]
                    gi.blit(self.sprites.getImage(6, 10.2), pos) # Arrow down
                    gi.blit(self.sprites.getImage(4, 1), [pos[0], pos[1] + self.sprites.cellSize[1]]) # hole
                    # 4
                    pos[0] += self.sprites.cellSize[0]
                    gi.blit(self.sprites.getImage(2, 0), pos) # Goon
                    gi.blit(self.sprites.getImage(6, 0), [pos[0], pos[1] - self.sprites.cellSize[1]]) # !
                    # Selection arrow 2
                    gi.blit(self.sprites.getImage(6, 8), [pos[0], pos[1] + self.sprites.cellSize[1]])

                elif trap_list[0].trap == "Portal":
                    gi.blit(self.sprites.getImage(6, trap_list[0].current[1]), pos)
                    gi.blit(self.sprites.getImage(3, 0), pos) # Player
                    pos[0] += self.sprites.cellSize[0]
                    gi.blit(self.sprites.getImage(6, 10.2), pos) # Arrow
                    pos[0] += self.sprites.cellSize[0]
                    gi.blit(self.sprites.getImage(4, 6), pos) # Question
            elif len(item_list) > 0: # Items
                w = (w -  len(item_list)*self.sprites.cellSize[0]) /2
                for i in range(len(item_list)):
                    pos = [w + cursor + offset_x + self.sprites.cellSize[0], (h + self.sprites.cellSize[1])/2 + offset_y]
                    gi.blit(self.sprites.getImage(5, item_list[i]), pos)
                    if self.DEBUGGING:
                        pygame.draw.rect(gi, (255,0,0), pos + self.sprites.cellSize, 1)
                    cursor += self.sprites.cellSize[0]



        gfinal.blit(gg, (0,0))
        gfinal.blit(gi, (0,0))
        return gfinal

        
        


    def getForegroundImage(self, center):
        # Draw the entities
        fg = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)

        offset_x = self.size[0]/2-(center[0]*self.sprites.cellSize[0])
        offset_y = self.size[1]/2-((len(self.map.cells[0])-center[1])*self.sprites.cellSize[1])

        arr = self.map.contents
        for entity in arr:
            x, y = entity.position
            if self.map.cells[x][y].visible != 0 or self.DEBUGGING:
                pos = (x*self.sprites.cellSize[0] + offset_x,(len(self.map.cells[0])-y)*self.sprites.cellSize[1] + offset_y)
                if entity.type == "Projectile":
                    fg.blit(self.sprites.getImage(6, 1), pos)
                elif entity.type == "Player":
                    if self.hiding:
                        fg.blit(self.sprites.getImage(3, 2), pos)
                    else:
                        fg.blit(self.sprites.getImage(3, 0 + (1 if self.bouncing else 0)), pos)
                elif entity.type == "Monster":
                    fg.blit(self.sprites.getImage(2, 0 + (1 if self.bouncing and entity.chasing else 0)), pos)
                    if entity.chasing:
                        fg.blit(self.sprites.getImage(6, 0), [pos[0], pos[1]-self.sprites.cellSize[1]])
                    elif len(entity.path) == 0 or entity.stunned > 0:
                        fg.blit(self.sprites.getImage(6, 4), pos)
                elif entity.type == "Trap":
                    if not entity.current is None:
                        fg.blit(self.sprites.getImage(entity.current[0], entity.current[1]), pos)
                elif entity.type == "Item":
                    fg.blit(self.sprites.getImage(4, 0), pos)
                if entity.hit:
                    fg.blit(self.sprites.getImage(6, 1), pos)

        return fg

    def getBackgroundImage(self, center):
        
        # Draw the map
        bg = pygame.Surface((self.size[0], self.size[1]))
        bg.fill((0,0,0))

        offset_x = self.size[0]/2-(center[0]*self.sprites.cellSize[0])
        offset_y = self.size[1]/2-((len(self.map.cells[0])-center[1])*self.sprites.cellSize[1])

        arr = self.map.cells
        for x in range(len(arr)):
            for y in range(len(arr[x])):
                if arr[x][y].revealed or self.DEBUGGING:
                    pos = [x*self.sprites.cellSize[0] + offset_x,(len(arr[x])-y)*self.sprites.cellSize[1] + offset_y]
                    bg.blit(self.sprites.getImage(1, arr[x][y].floortype), pos)
                    for entity in arr[x][y].contents:
                        if entity.type == "Decor":
                            bg.blit(self.sprites.getImage(entity.category, entity.index), pos)
                    if arr[x][y].exit:
                        bg.blit(self.sprites.getImage(4, 3), pos)
                    elif arr[x][y].wall:
                        bg.blit(self.sprites.getImage(0, arr[x][y].walltype), pos)
                    # Shadow
                    shadow = pygame.Surface(self.sprites.cellSize, pygame.SRCALPHA)
                    shadow.fill((0, 0, 0, 255 * (1 - max(.3, arr[x][y].visible))))
                    bg.blit(shadow, pos)
                    if self.DEBUGGING and arr[x][y].visible != 0:
                        pygame.draw.rect(bg, (255,0,0), pos + self.sprites.cellSize, 1)

        return bg

    def getPercentColour(self, current_v, max_v):
        # Green = 100%
        # Red <= 30%
        r = 255*(max_v-current_v)/max_v
        g = 255*current_v/max_v
        m = max(r, g)
        r = r / m * 255
        g = g / m * 255
        b = 0
        return (r, g, b)