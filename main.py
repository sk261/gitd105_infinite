import math
import random
import resources
import game

import pygame
from pygame import mixer, time

WINDOW_SIZE = [800, 600]


# Intialize the pygame
pygame.init()

# create the screen
screen = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))

# Framerate
clock = pygame.time.Clock()


# Caption and Icon
pygame.display.set_caption("Endless Escape")
sprites = resources.SpriteSheet()
pygame.display.set_icon(sprites.getImage(3, 0))

session = game.Game(sprites)

# Game Loop
running = True
while running:

    session.tick()
    
    triggers = {}
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                triggers["left"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                triggers["right"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                triggers["up"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                triggers["down"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_1:
                triggers["1"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_2:
                triggers["2"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_3:
                triggers["3"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_SPACE:
                triggers["space"] = event.type == pygame.KEYDOWN
            if event.key == pygame.K_ESCAPE:
                # You get nothing. Close the fucking screen
                running = False
                break
    session.triggerInput(triggers)

    if session.graphics_updates:
        screen.blit(session.draw(), [0,0])
        pygame.display.update()
    clock.tick(60)
