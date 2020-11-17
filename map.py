import random
random.seed()
import entity

# For debugging
import math

class Cell:
    def __init__(self, isWall):
        self.wall = isWall
        self.contents = []
        self.revealed = False
        self.floortype = 0
        self.walltype = 0
        self.exit = False
        self.decor = []

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

        self.nodes = {}
        self.connections = {}

        #Increase this number for more paths
        self.diversity = self.size[0]+self.size[1]

        self.OPPOSITE = {"N":"S","S":"N","E":"W","W":"E"}
        self.DX = {"N":0, "S":0, "E":1, "W":-1}
        self.DY = {"N":1, "S":-1, "E":0, "W":0}

    def generatedSize(self, i = -1):
        if i == -1:
            return [len(self.cells), len(self.cells[0])]
        else:
            return [len(self.cells), len(self.cells[0])][i]

    def coordToGraphic(self, x, y):
        return [(2*x)+1, (2*y)+1]

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

    def revealCells(self, position):
        pass

    def _getCellWallMap(self):
        ret = []
        for x in range(self.size[0]):
            tempL, tempM, tempR = [], [], []
            for y in range(self.size[1]):
                
                if y == 0:
                    if x == 0:
                        tempL.append(True)
                    tempM.append(self.cells[x][y].WALLS["S"])
                    tempR.append(True)

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
            ret.append(tempM)
            ret.append(tempR)
        return ret
        

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

    def entitySeesEntity(self, looker, target, direction):
        arr = list(self.DX.keys())
        if direction in self.DX:
            arr = [direction]
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
                if not self._is_wall(current_path[-1][0], current_path[-1][1], d):
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

        print("Error during pathfinding")
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
                        cell.walltype = potential
                else:
                    # Walls
                    if random.randrange(5) == 0:
                        self.cells[x][y].floortype = random.choice([2,3,5,6,7,8])
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
