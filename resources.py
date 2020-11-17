import pygame

class SpriteSheet:

    def __init__(self):
        sheetIMG = None
        try:
            sheetIMG = pygame.image.load('assets.png').convert_alpha()
        except pygame.error as e:
            print("Error loading spritesheet")
            raise SystemExit(e)
        self.sheet = []

        self.cellSize = [24, 24]
        self.width = int(sheetIMG.get_width() / self.cellSize[0])
        self.height = int(sheetIMG.get_height() / self.cellSize[1])

        for typeID in range(self.height):
            insert = []
            for index in range(self.width):
                base = []
                # 0 -> normal
                base.append(self.loadImage(typeID, index, sheetIMG, 0, False))
                # 1,2,3 -> rotate clockwise by 90, 180, and 270.
                base.append(self.loadImage(typeID, index, sheetIMG, 90, False))
                base.append(self.loadImage(typeID, index, sheetIMG, 180, False))
                base.append(self.loadImage(typeID, index, sheetIMG, 270, False))
                # 4 -> flip
                base.append(self.loadImage(typeID, index, sheetIMG, 0, True))
                
                insert.append(base)
            self.sheet.append(insert)
        

    def getImage(self, typeID, index):
        r = int(index % 1 * 11)
        return self.sheet[typeID][int(index)][r]
        
    def loadImage(self, typeID, index, sheetIMG, r, f):
        rect = pygame.Rect(index*24, typeID*24, 24, 24)
        image = pygame.Surface(rect.size, pygame.SRCALPHA, 32).convert_alpha()
        image.blit(sheetIMG, (0, 0), rect)
        image = pygame.transform.rotate(image, -r)
        if f:
            image = pygame.transform.flip(image, False, True)
        return image
