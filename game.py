import map
import pygame
import entity
import random
import math
random.seed()
import time as _time
time = lambda: int(round(_time.time() * 1000))


class Game:
    def __init__(self):
        self.player = entity.Player()
        self.direction = ""
        self.player_moves = 0

        self.items = 0 # TODO
        self.map = map.Map()
        self.map.generateMap([10,10])
        self.player.position = self.map.coordToGraphic(10,10)
        # self.map.addEntity(self.player)
        self.map.generateMonsters(10, entity.DEFAULT_MONSTER)
        self.level = 0

        self.currentTriggers = []
        self.graphics_updates = True
        self.bg_image = None
        self.fg_image = None
        self.last_image = None
        self.Cooldown = 0
        self.maxCooldown = 200
    
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
        if self.direction != "":
            playerTurn = True
            self.graphics_updates = True
            """
            # Player movement
            if self.map.moveEntity(self.player, self.direction):
                self.player_moves += 1
                self.graphics_updates = True
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
            """

                

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


                    dirs = list(self.map.DX.keys())
                    random.shuffle(dirs)
                    """ # Removed for newer version
                    if entity.path[0] in dirs:
                        dirs.remove(entity.path[0])
                        dirs = [entity.path[0]] + dirs
                    if entity.lastD != "":
                        dirs.remove(self.map.OPPOSITE[entity.lastD])
                        dirs.append(self.map.OPPOSITE[entity.lastD])
                    for d in dirs:
                        if self.map.moveEntity(entity, d):
                            if len(entity.path) > 1:
                                if self.map.nodes[entity.path[1]] == entity.position:
                                    entity.path.pop(0)
                                    entity.path.pop(0)
                            self.graphics_updates = True
                            entity.lastD = d
                            break
                    """
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
            self.bg_image = self.getBackgroundImage(0,0)
            self.fg_image = self.getForegroundImage(0,0)

        ret = pygame.Surface((self.size[0], self.size[1]))
        ret.blit(self.bg_image, (0, 0))
        ret.blit(self.fg_image, (0, 0))
        
        return ret

    def getForegroundImage(self, x, y):
        # Draw the entities
        fg = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA, 32)

        arr = self.map.contents
        for entity in arr:
            x, y = entity.position
            rgb = (255,0,0)
            if entity.type == "Player":
                rgb = (0,255,0)
            pygame.draw.rect(fg, rgb, (x*5,(len(self.map.cells[0])-y)*5,5,5))    

        return fg

    def getBackgroundImage(self, x, y):
        # Draw the map
        bg = pygame.Surface((self.size[0], self.size[1]))
        bg.fill((200,200,200))

        arr = self.map.cells
        for x in range(len(arr)):
            for y in range(len(arr[x])):
                if arr[x][y].wall:
                    pygame.draw.rect(bg, (0,0,0), (x*5,(len(arr[x])-y)*5,5,5))    
                else:
                    pygame.draw.rect(bg, (200,200,200), (x*5,(len(arr[x])-y)*5,5,5))    
        return bg