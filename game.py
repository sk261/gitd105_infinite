import map
import pygame
import entity
import math
import random
random.seed()
import time as _time
time = lambda: int(round(_time.time() * 1000))


class Game:
    def __init__(self, spritesheet):
        self.player = entity.Player()
        self.direction = ""
        self.player_moves = 0

        self.items = 0 # TODO
        self.map = map.Map()
        self.map.generateMap([10,10])
        self.player.position = self.map.coordToGraphic(10,10)
        self.map.addEntity(self.player)
        self.map.revealCellsFromEntity(self.player)
        self.map.generateMonsters(10, entity.DEFAULT_MONSTER)
        self.level = 0

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

        self.currentCellContents = []
        self.DEBUGGING = False
    
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
        if '1' in keys:
            # TODO
            pass
        if '2' in keys:
            # TODO
            pass
        if '3' in keys:
            # TODO
            pass
        if 'space' in keys:
            # TODO
            pass
        if 'exit' in keys:
            # TODO - end game
            pass
        self.currentTriggers = []
            

    
    def tick(self):
        self.size = pygame.display.get_surface().get_size()

        #TODO Have characters bounce and move

        # Turn only triggers when player performs an action
        if time() < self.Cooldown:
            return False

        playerTurn = False

        self.handleControls()
        if self.direction != "" and not self.waitForDialogue:
            self.graphics_updates = True
            
            # Player movement
            if self.map.moveEntity(self.player, self.direction):
                self.map.clearVisibility()
                self.map.revealCellsFromEntity(self.player)
                self.currentCellContents = self.map.cells[self.player.position[0]][self.player.position[1]].contents
                self.player_moves += 1
                self.graphics_updates = True
                # Check for traps
                for entity in self.currentCellContents:
                    if entity.type == "Trap":
                        self.waitForDialogue = entity.requires_dialogue
                        if self.waitForDialogue:
                            pass
                # Player moved successfully, entity target check for player
                for entity in self.map.contents:
                    if not entity.moving:
                        continue
                    if self.map.entitySeesEntity(entity, self.player, entity.lastD):
                        entity.changeTarget([self.player.position[0], self.player.position[1]])
                        entity.chasing = True

            if self.player_moves >= self.player.speed:
                self.player_moves = 0
                playerTurn = True
        
        self.direction = ""
            

                

        if playerTurn:
            self.Cooldown = time() + self.maxCooldown
            arr = self.map.contents
            for entity in arr:
                if not entity.moving:
                    continue
                # Target selection (normal travel)

                for s in range(entity.speed):
                    if entity.target == entity.position or entity.target == None:
                        if self.map.entitySeesEntity(entity, self.player, entity.lastD):
                            entity.changeTarget([self.player.position[0], self.player.position[1]])
                            entity.chasing = True
                        elif entity.position == entity.home:
                            entity.changeTarget(self.map.getRandomRoomOrElsePoint(entity.home))
                            entity.chasing = False
                        else:
                            entity.changeTarget(entity.home)
                            entity.chasing = False
                    if len(entity.path) == 0:
                        # entity.path = self.map.pathToPoint(entity.position, entity.target, entity.lastD)
                        entity.path = self.map.pathToPoint(entity.position, entity.target)

                    # Newer version
                    acted = False
                    while not acted:
                        acted = True
                        dx, dy = 0, 0
                        while dx == 0 and dy == 0:
                            if len(entity.path) == 0:
                                entity.changeTarget(self.map.getRandomRoomOrElsePoint(entity.home))
                                entity.path = self.map.pathToPoint(entity.position, entity.target)
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
                                acted = False
                                entity.changeTarget(self.map.getRandomRoomOrElsePoint(entity.home))
                                # Something's blocking TODO (probably attack)
                            
                        

    def draw(self):
        if self.graphics_updates:
            self.graphics_updates = False
            self.bg_image = self.getBackgroundImage(self.player.position)
            self.fg_image = self.getForegroundImage(self.player.position)
            self.gg_image = self.getGUIImage(None)

        ret = pygame.Surface((self.size[0], self.size[1]))
        ret.blit(self.bg_image, (0, 0))
        ret.blit(self.fg_image, (0, 0))
        ret.blit(self.gg_image, (0, 0))
        
        return ret

    def getGUIImage(self, options):
        gg = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)
        gfinal = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)
        gi = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)
        gg.set_alpha(200)
        panelBG = self.sprites.getImage(1, 1)

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
        halfHeart = (self.player.health % 2 == 0)
        for n in range(3):
            off = (n-1) + 1/2
            i = 4
            if n < full_hearts:
                i = 2
            elif n == full_hearts and halfHeart:
                i = 3
            gi.blit(self.sprites.getImage(5, i), (TL[0] + w/2 - off*self.sprites.cellSize[0], cursor))
        # Current Armor
        cursor += self.sprites.cellSize[1]
        gi.blit(self.sprites.getImage(5, self.player.armor), (TL[0] + w/2 - self.sprites.cellSize[0]/2, cursor))
        cursor += self.sprites.cellSize[1]
        pygame.draw.rect(
            gi,
            self.getPercentColour(self.player.armor_quality, self.player.armor_max_quality),
            pygame.Rect(TL[0] + w/2 - self.sprites.cellSize[0]/2, cursor, self.sprites.cellSize[0], 3))
        # Boxes
        cursor += 5
        for item in range(self.player.max_inventory):
            pygame.draw.rect(
                gg,
                (100, 100, 100),
                pygame.Rect(TL[0] + w/10, cursor, 8*w/10, self.sprites.cellSize[1]*1.5))
            pygame.draw.rect(
                gg,
                (150, 150, 150),
                pygame.Rect(TL[0] + w/10 + 2, cursor + 2, 8*w/10 - 4, self.sprites.cellSize[1]*1.5 - 4))
            if item < len(self.player.inventory):
                pass # TODO: Draw picked up items
            cursor += 2*self.sprites.cellSize[1]

        # Bottom panel prep
        revealed = False
        item_list = []
        trap_list = []
        for content in self.currentCellContents:
            if content.type == "Trap":
                revealed = True
                trap_list.append(content.current)
                print("Trapped!")
            elif content.type == "Item":
                revealed = True
                item_list.append(content.index) # Add item to the list

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
           
            gi.blit(self.sprites.getImage(5, self.player.armor), (TL[0] + w/2 - self.sprites.cellSize[0]/2, cursor))
            # Bottom panel FG
            # TODO Add various messages and only draw this if one is available (passed through the 'options' param)
            if len(trap_list) > 0:
                pass
                # TODO: Trap first
            elif len(item_list) > 0:
                for i in range(len(item_list)):
                    pass # TODO: Draw items to be picked up
                # TODO: Okay you can have your items, if you must.



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
                if entity.type == "Player":
                    fg.blit(self.sprites.getImage(3, 0), pos)
                elif entity.type == "Monster":
                    fg.blit(self.sprites.getImage(2, 0), pos)
                elif entity.type == "Trap":
                    if not entity.current is None:
                        fg.blit(self.sprites.getImage(entity.current[0], entity.current[1]), pos)
                elif entity.type == "Item":
                    fg.blit(self.sprites.getImage(4, 0), pos)
                elif entity.type == "Decor":
                    pass

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