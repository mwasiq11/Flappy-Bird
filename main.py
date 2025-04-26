import os
import random
import sys
import pygame
from pygame.locals import *

# Game Screen FPS,Height,Width
fps = 60
screenWidth = 500
screenHeight = 700
groundY = screenHeight * 0.8

# File Paths
player = 'images/bird.png'
background = 'images/background.png'
pipe = 'images/pipe.png'
ground = 'images/ground.png'
message = 'images/start.png'
number_path = 'images/'

# Load Assets Section
gameImages = {}
gameSound = {}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
fpsClock = pygame.time.Clock()
pygame.display.set_caption("Flappy Bird")

# images section
gameImages['background'] = pygame.image.load(background).convert()
gameImages['message'] = pygame.image.load(message).convert_alpha()
gameImages['player'] = pygame.image.load(player).convert_alpha()
gameImages['base'] = pygame.image.load(ground).convert_alpha()
gameImages['pipe'] = (
    pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(), 180),
    pygame.image.load(pipe).convert_alpha()
)
gameImages['numbers'] = []

for i in range(10):
    img = pygame.image.load(os.path.join(number_path, f'{i}.png')).convert_alpha()
    img = pygame.transform.smoothscale(img, (30, 40))
    gameImages['numbers'].append(img)

# sound effect wing,point,flap
gameSound['wing'] = pygame.mixer.Sound('sound/wing.wav')
gameSound['point'] = pygame.mixer.Sound('sound/point.wav')
gameSound['hit'] = pygame.mixer.Sound('sound/hit.wav')


def welcomeScreen():
    playerX = screenWidth // 5
    playerY = screenHeight - gameImages['player'].get_height() // 2
    messageX = (screenWidth - gameImages['message'].get_width()) // 2
    messageY = screenHeight * 0.25
    baseX = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        screen.blit(gameImages['background'], (0, 0))
        screen.blit(gameImages['message'], (messageX, messageY))
        screen.blit(gameImages['player'], (playerX, playerY))
        screen.blit(gameImages['base'], (baseX, groundY))
        pygame.display.update()
        fpsClock.tick(fps)


def mainGame():
    score = 0
    playerx = int(screenWidth / 5)
    playery = int(screenWidth / 2)
    basex = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [
        {'x': screenWidth + 200, 'y': newPipe1[0]['y']},
        {'x': screenWidth + 200 + screenWidth / 2, 'y': newPipe2[0]['y']}
    ]
    lowerPipes = [
        {'x': screenWidth + 200, 'y': newPipe1[1]['y']},
        {'x': screenWidth + 200 + screenWidth / 2, 'y': newPipe2[1]['y']}
    ]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    playerFlapAccv = -8
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    gameSound['wing'].stop()
                    gameSound['wing'].play()
                    pygame.time.delay(30)  # delay for having smoother flap 

        if isCollide(playerx, playery, upperPipes, lowerPipes):
            return

        playerMidPos = playerx + gameImages['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + gameImages['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                gameSound['point'].stop()
                gameSound['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False

        playerHeight = gameImages['player'].get_height()
        playery = playery + min(playerVelY, groundY - playery - playerHeight)

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        if upperPipes[0]['x'] < -gameImages['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        screen.blit(gameImages['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            screen.blit(gameImages['pipe'][0], (upperPipe['x'], upperPipe['y']))
            screen.blit(gameImages['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        screen.blit(gameImages['base'], (basex, groundY))
        screen.blit(gameImages['player'], (playerx, playery))

        # to count Score
        myDigits = [int(x) for x in str(score)]
        totalWidth = sum(gameImages['numbers'][d].get_width() for d in myDigits)
        Xoffset = (screenWidth - totalWidth)//2

        for digit in myDigits:
            screen.blit(gameImages['numbers'][digit], (Xoffset, screenHeight * 0.1))
            Xoffset += gameImages['numbers'][digit].get_width()

        pygame.display.update()
        fpsClock.tick(fps)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > groundY - 25 or playery < 0:
        gameSound['hit'].stop()
        gameSound['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = gameImages['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y']) and abs(playerx - pipe['x']) < gameImages['pipe'][0].get_width():
            gameSound['hit'].stop()
            gameSound['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + gameImages['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < gameImages['pipe'][0].get_width():
            gameSound['hit'].stop()
            gameSound['hit'].play()
            return True

    return False


def getRandomPipe():
    pipeHeight = gameImages['pipe'][0].get_height()
    offset = screenHeight / 3
    y2 = offset + random.randrange(0, int(screenHeight - gameImages['base'].get_height() - 1.2 * offset))
    pipeX = screenWidth + 10
    y1 = pipeHeight - y2 + offset
    return [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]


# Main game loop
if __name__ == "__main__":
    while True:
        welcomeScreen()
        mainGame()
