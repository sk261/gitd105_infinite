import random
random.seed()
import entity

# For debugging
import math

class Cell:
    def __init__(self, isWall):
        self.wall = isWall
        self.blocksVision = isWall
        self.contents = []
        self.revealed = False
        self.visible = 0
        self.floortype = 0
        self.walltype = 0
        self.exit = False
        self.decor = []

    def setWallType(self, _id):
        self.walltype = _id
        self.blocksVision = not _id in [2, 4, 6]

class _Cell:
    def __init__(self):
        self.WALLS = {"N":True, "S":True, "E":True, "W":True}
        self.visited = False
        self.contents = []

class Map:
    def __init__(self):
        self.cells = []
        self.size = [20,20]
        self.contents = []
        self.rooms = []
        self.hallway_size = 2
        self.visibleCells = []

        self.nodes = {}
        self.connections = {}

        #Increase this number for more paths
        self.diversity = self.size[0]+self.size[1]

        self.OPPOSITE = {"N":"S","S":"N","E":"W","W":"E"}
        self.SIDES = {"N":["W", "E"],"S":["W", "E"],"E":["N", "S"],"W":["N", "S"]}
        self.DX = {"N":0, "S":0, "E":1, "W":-1}
        self.DY = {"N":1, "S":-1, "E":0, "W":0}

    def generatedSize(self, i = -1):
        if i == -1:
            return [len(self.cells), len(self.cells[0])]
        else:
            return [len(self.cells), len(self.cells[0])][i]

    def coordToGraphic(self, x, y):
        return [((self.hallway_size+1)*x)+int((self.hallway_size+1)/2), ((self.hallway_size+1)*y)+int((self.hallway_size+1)/2)]

    def addEntity(self, entity):
        pos = entity.position
        if self.cells[pos[0]][pos[1]].wall:
            return False
        valid = True
        if len(self.cells[pos[0]][pos[1]].contents) > 0:
            for n in self.cells[pos[0]][pos[1]].contents:
                if n.blocking:
                    valid = False
        if valid:
            self.contents.append(entity)
            self.cells[pos[0]][pos[1]].contents.append(entity)
            return True
        return False
    
    def clearVisibility(self):
        for cell in self.visibleCells:
            cell.visible = 0
        self.visibleCells = []

    def getCellsFromEnttiy(self, entity, dist, d):
        ret = []

        pos = entity.position
        y_mod = True if self.DY[d] != 0 else False
        x_mod = self.DY[d] if self.DX[d] == 0 else self.DX[d]

        slope_bounds = [-1, 1]
        for r in range(1, dist+1):
            # r is the x step

            new_slopes = [el for el in slope_bounds]
            for n in range(int((len(slope_bounds)+1)/2)):
                # Get every pair of slopes.
                _max = int(slope_bounds[2*n + 1] * r)
                _min = int(slope_bounds[2*n] * r)
                for _y in range(_min, _max+1):
                    if y_mod:
                        _cpY = pos[1] +  r*x_mod
                        _cpX = pos[0] + _y
                    else:
                        _cpY = pos[1] + _y
                        _cpX = pos[0] + r*x_mod

                    if self.cellExists(_cpX, _cpY):
                        ret.append([_cpX, _cpY])

                    blocked = not self.cellExists(_cpX, _cpY) or self.cells[_cpX][_cpY].blocksVision
                    if blocked:
                        r_mod = -1 if _y < 0 else 1
                        if _y == _max: #reduce max
                            new_slopes[-1] = (_y-.5)/(r+(.5 * r_mod))
                        elif _y == _min: #reduce min
                            new_slopes[0] = (.5+_y)/(r+(-.5 * r_mod))
                        else: # new pair
                            new_slopes.insert(2*n+1, (.5+_y)/(r-.5)) # min
                            new_slopes.insert(2*n+1,  (_y-.5)/(r+.5)) # max
            slope_bounds = new_slopes
            change = True
            while change:
                change = False
                new_slopes = [el for el in slope_bounds]
                # Slope checker:
                for n in range(int((len(slope_bounds)+1)/2)):
                    _max = slope_bounds[2*n + 1]
                    _min = slope_bounds[2*n]
                    if _min == _max: # delete both
                        change = True
                        new_slopes[2*n] = None
                        new_slopes[2*n+1] = None
                        break
                    elif _min > _max and n > 0 and 2*n+2 < len(slope_bounds): #swap their places and delete surrounding ones
                        change = True
                        new_slopes[2*n], new_slopes[2*n+1] = new_slopes[2*n+1], new_slopes[2*n]
                        new_slopes[2*n-1], new_slopes[2*n+2] = None, None
                        break
                    elif _min > _max and n == 0 and len(slope_bounds) > 2:
                        change = True
                        new_slopes[0] = max(new_slopes[0], new_slopes[2])
                        new_slopes[1], new_slopes[2] = None, None
                        break
                    elif _min > _max and 2*n + 2 == len(slope_bounds) and len(slope_bounds) > 2:
                        change = True
                        new_slopes[-1] = min(new_slopes[-1], new_slopes[-3])
                        new_slopes[-2], new_slopes[-3] = None, None
                        break
                    elif _min > _max:
                        change = True
                        new_slopes[2*n] = None
                        new_slopes[2*n+1] = None
                        break
                slope_bounds = [el for el in new_slopes if not el is None]
        return ret

    def revealCellsFromEntity(self, entity, dist = 5):
        pos = entity.position
        cells = []
        cells.append(pos)
        for d in self.DX.keys():
            cells = cells + self.getCellsFromEnttiy(entity, dist, d)
        for cell in cells:
            self.cells[cell[0]][cell[1]].revealed = True
            self.cells[cell[0]][cell[1]].visible =  (math.dist((0, 0), (dist, dist)) - math.dist(cell, pos)) / math.dist((0, 0), (dist, dist))

    def removeEntity(self, entity):
        if entity in self.contents:
            self.contents.remove(entity)
        x, y = entity.position
        if entity in self.cells[x][y].contents:
            self.cells[x][y].contents.remove(entity)
    
    def moveEntity(self, entity, d):
        for target in self.contents:
            if entity == target:
                cell = self.cells[target.position[0]][target.position[1]]
                nx = self.DX[d] + target.position[0]
                ny = self.DY[d] + target.position[1]
                if nx < 0 or ny < 0 or nx >= self.generatedSize(0) or ny >= self.generatedSize(1):
                    return False
                newcell = self.cells[nx][ny]
                if newcell.wall:
                    return False
                for n in newcell.contents:
                    if n.blocking:
                        return False
                cell.contents.remove(target)
                newcell.contents.append(target)
                target.position = [nx, ny]
                return True


    # Turns a wall chart into a cell map
    def _getCellWallMap(self):
        cell_size = self.hallway_size
        ret = []
        for x in range(self.size[0]):
            tempL, tempM, tempR = [], [], []
            for y in range(self.size[1]):

                if y == 0:
                    if x == 0:
                        tempL.append(True)
                    tempM.append(self.cells[x][y].WALLS["S"])
                    tempR.append(True)

                for n in range(cell_size):
                    if x == 0:
                        tempL.append(self.cells[x][y].WALLS["W"])
                    tempM.append(False)
                    tempR.append(self.cells[x][y].WALLS["E"])
                
                if x == 0:
                    tempL.append(True)
                tempM.append(self.cells[x][y].WALLS["N"])
                tempR.append(True)

            if x == 0:
                ret.append(tempL)
            for n in range(cell_size):
                ret.append(tempM)
            ret.append(tempR)
        return ret
        
    def cellExists(self, x, y):
        return x >= 0 and x < len(self.cells) and y >= 0 and y < len(self.cells[x])

    def getCellContent(self, x, y):
        if self.cells[x][y].wall:
            return False
        return self.cells[x][y].contents

    def getRandomRoomOrElsePoint(self, excludeRoom = False):
        if excludeRoom == False and self.rooms > 0:
            return self.rooms[random.randrange(len(self.rooms))]
        else:
            if len(self.rooms) > 0:
                random.shuffle(self.rooms)
                for n in self.rooms:
                    if n == excludeRoom:
                        continue
                    else:
                        return n
            while(True):
                pos =  [random.randrange(self.generatedSize(0)), random.randrange(self.generatedSize(1))]
                if not self.cells[pos[0]][pos[1]].wall:
                    return pos

    def entitySeesEntity(self, looker, target, lastD):
        arr = list(self.DX.keys())
        if lastD in self.DX:
            arr = [self.OPPOSITE[lastD]]
        for d in arr: 
            px, py = looker.position
            while not self.cells[px][py].wall:
                if target in self.cells[px][py].contents:
                    return True
                else:
                    px += self.DX[d]
                    py += self.DY[d]
        return False

    
    def generateMonsters(self, quantity, monster):
        for n in range(quantity):
            temp = monster.clone()
            if len(self.rooms) > 0:
                temp.home = self.rooms[random.randrange(len(self.rooms))]
            pos =  [random.randrange(self.generatedSize(0)), random.randrange(self.generatedSize(1))]
            while temp is not False:
                temp.position = pos
                if self.addEntity(temp):
                    temp = False
                pos = [random.randrange(self.generatedSize(0)), random.randrange(self.generatedSize(1))]

                
    def cellHasType(self, position, entityType):
        for entity in self.cells[position[0]][position[1]].contents:
            if entity.type == entityType:
                return entity
        return False
    
    def swapEntities(self, entityA, entityB):
        Ax, Ay = entityA.position
        Bx, By = entityB.position
        self.cells[Ax][Ay].contents.remove(entityA)
        self.cells[Bx][By].contents.remove(entityB)
        self.cells[Ax][Ay].contents.append(entityB)
        self.cells[Bx][By].contents.append(entityA)
        entityA.position = [Bx, By]
        entityB.position = [Ax, Ay]

        

    def pathToPoint(self, start, end):
        pq = {}

        pq[0] = [[start]]
        found = False
        visited = [start]
        error_handling = ""
        while not found and len(pq) > 0:
            cpi = sorted(pq)[0]
            current_path = pq[cpi][0]
            del pq[cpi][0]
            if len(pq[cpi]) == 0:
                del pq[cpi]
            if current_path[-1] == end:
                return current_path
            for d in self.DX:
                if self._is_walkable_NPC(current_path[-1][0], current_path[-1][1], d):
                    pos = [current_path[-1][0], current_path[-1][1]]
                    pos[0] += self.DX[d]
                    pos[1] += self.DY[d]
                    if not pos in visited:
                        visited.append(pos)
                        new_path = current_path.copy()
                        new_path.append(pos)
                        if not cpi + 1 in pq:
                            pq[cpi + 1] = []
                        pq[cpi+1].append(new_path)
            if len(pq) == 0:
                error_handling = current_path

        print("No path found")
        return False

    def _make_nodes(self):
        self.nodes = {}
        self.connections = {}
        # Find all nodes
        counter = 1
        # Add rooms
        for n in self.rooms:
            self.nodes[counter] = n
            counter += 1
        for x in range(1, len(self.cells)-1):
            for y in range(1, len(self.cells[0])-1):
                if not self._is_wall(x, y):
                    c = 0
                    for n in self.DX:
                        if not self._is_wall(x, y, n):
                            c += 1
                    if c > 2:
                        if not [x, y] in self.rooms:
                            self.nodes[counter] = [x, y]
                            counter += 1
  
    def _is_blocked(self, x, y, d = None):
        _x = x
        _y = y
        if d in self.DX.keys():
            _x += self.DX[d]
            _y += self.DY[d]
        if _x < 0 or _x >= len(self.cells) or _y < 0 or _y >= len(self.cells[_x]):
            return True
        else:
            for entity in self.cells[_x][_y].contents:
                if entity.blocking:
                    return True
            return self.cells[_x][_y].wall


    def _is_wall(self, x, y, d = None):
        _x = x
        _y = y
        if d in self.DX.keys():
            _x += self.DX[d]
            _y += self.DY[d]
        if _x < 0 or _x >= len(self.cells) or _y < 0 or _y >= len(self.cells[_x]):
            return True
        else:
            return self.cells[_x][_y].wall
    
    def _is_walkable_row_NPC(self, x, y, d):
        _x, _y = x + self.DX[d], y + self.DY[d]
        _L, _R = self.SIDES[d]
        L = self._is_walkable_NPC(x, y, _L)
        M = self._is_walkable_NPC(x, y, d)
        R = self._is_walkable_NPC(x, y, _R)
        return (L and M and R)

    
    def _is_walkable_NPC(self, x, y, d):
        if self._is_wall(x, y, d):
            return False
        _x = x + self.DX[d]
        _y = y + self.DY[d]
        for entity in self.cells[_x][_y].contents:
            if entity.type == "Trap" or entity.type == "Item":
                return False
        return True




    def generateMap(self, start):
        self.cells = []
        for x in range(self.size[0]):
            temp = []
            for y in range(self.size[1]):
                temp.append(_Cell())
            self.cells.append(temp)
        self.carvePath(start)
        for n in range(self.diversity):
            x, y = random.randrange(self.size[0]), random.randrange(self.size[1])
            choices = self.cells[x][y].WALLS
            keys = []
            for z in choices:
                if choices[z]:
                    keys.append(z)
            if len(keys) == 0:
                continue
            key = keys[random.randrange(len(keys))]
            nx = self.DX[key] + x
            ny = self.DY[key] + y
            if nx < 0 or ny < 0 or nx >= self.size[0] or ny >= self.size[0]:
                continue
            self.cells[x][y].WALLS[key] = False
            self.cells[nx][ny].WALLS[self.OPPOSITE[key]] = False
        # Turn into mono-square pieces
        arr = self._getCellWallMap()
        self.cells = []
        for x in range(len(arr)):
            temp = []
            for y in range(len(arr[x])):
                temp.append(Cell(arr[x][y]))
            self.cells.append(temp)
        
        for x in range(1, len(self.cells)-1):
            for y in range(1, len(self.cells[0])-1):
                    walls = 0
                    for n in self.DX:
                        walls += 1 if self.cells[x+self.DX[n]][y+self.DY[n]].wall else 0
                    if walls == 0 and self.cells[x][y].wall: #Rooms
                        self.rooms.append([x, y])
                        self.cells[x][y].wall = False
                        self.cells[x][y].blocksVision = False
                        """
                    elif walls == 3 and not self.cells[x][y].wall: #Dead ends, rooms for now.
                        self.rooms.append([x, y])
                        """

        self._make_nodes()
        
        
        
        # Special walls and floors, and items
        for x in range(len(self.cells)):
            for y in range(len(self.cells[x])):
                cell = self.cells[x][y]
                if cell.wall:
                    potential = 0
                    N, S, E, W = [self._is_wall(x, y, d) for d in ["N", "S", "E", "W"]]
                    if N + S + E + W == 4:
                        continue
                    elif N + S + E + W == 1:
                        #Only one adjacent wall
                        if N or E or W:
                            potential = random.choice([2, 3, 4, 6])
                    elif N + S + E + W == 2:
                        if E + W == 2:
                            # Straight horizontal
                            potential = random.choice([3, 5])
                        elif N + S == 2:
                            # Straight vertical
                            potential = random.choice([2, 4, 6])
                        else:
                            # Corner
                            potential = random.choice([2, 4, 6])
                    elif N + S + E + W == 3:
                        potential = random.choice([2,4,6])
                    if random.randrange(8) == 0:
                        cell.setWallType(potential)
                else:
                    # Special Floor
                    if random.randrange(5) == 0:
                        self.cells[x][y].floortype = random.choice([2,3,5,6,7,8])
                    N, S, E, W = [self._is_walkable_row_NPC(x, y, d) for d in ["N", "S", "E", "W"]]
                    # Chek if the area is pasable.
                    if (N or S) and (E or W):
                        # Place item
                        if random.randrange(50) == 0:
                            item = entity.Item(random.choice([0,1,5,6,7,8,9,10,11]))
                            item.position = [x,y]
                            self.addEntity(item)
                        elif random.randrange(50) == 0:
                            # Traps
                            trap = entity.Trap(random.choice(list(entity.TRAPS.keys())))
                            trap.position = [x, y]
                            self.addEntity(trap)


        # Make carpetted rooms
        for room in self.rooms:
            if random.randrange(3) == 0:
                self.cells[room[0]][room[1]+1].floortype = 9
                self.cells[room[0]+1][room[1]+1].floortype = 9.1
                self.cells[room[0]+1][room[1]].floortype = 9.2
                self.cells[room[0]][room[1]].floortype = 9.3
        
        # Decor / Blood


        # Exit
        exit_spots = []
        for x in range(len(self.cells)):
            y = len(self.cells[x]) - 1
            N, S, E, W = [self._is_wall(x, y, d) for d in ["N", "S", "E", "W"]]
            if not S:
                exit_spots.append(x)
        exit_spot = random.choice(exit_spots)

        self.cells[exit_spot][len(self.cells[exit_spot]) - 1].exit = True



    def carvePath(self, point):
        self.cells[point[0]][point[1]].visited = True
        arr = list(self.DX.keys())
        random.shuffle(arr)
        for key in arr:
            if not self.cells[point[0]][point[1]].WALLS[key]:
                continue
            nx = self.DX[key] + point[0]
            ny = self.DY[key] + point[1]
            if nx < 0 or ny < 0 or nx >= self.size[0] or ny >= self.size[0]:
                continue

            if not self.cells[nx][ny].visited:
                self.cells[point[0]][point[1]].WALLS[key] = False
                self.cells[nx][ny].WALLS[self.OPPOSITE[key]] = False
                self.carvePath([nx, ny])
