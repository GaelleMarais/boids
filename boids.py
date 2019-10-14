#!/usr/bin/env python
# Boid implementation in Python using PyGame
# Ben Dowling - www.coderholic.com
import pygame
from pygame import *
import sys, random, math


pygame.init()

size = width, height = 1800, 900
boid_width = 50
boid_height = 37
flower_width = 50
flower_height = 50
border = 35
black = 0, 0, 0
white = 255, 255, 255

numBoids = 100
numFlowers = 5
boids = []
walls = []
flowers = []

class Wall:
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

class Boid:
    def __init__(self, x, y, boid_width, boid_height, velocity_max):
        self.x = x
        self.y = y
        self.width = boid_width
        self.height = boid_height
        self.velocity_max = velocity_max
        self.velocityX = random.randint(1, 10) / 10.0
        self.velocityY = random.randint(1, 10) / 10.0
        self.state = "moving"

    def is_on_wall(self, walls):
        for wall in walls:
            if self.x < wall.x2 and self.x > wall.x1 - self.width and self.y < wall.y2 and self.y > wall.y1 - self.height:
                return True
        return False

    "Return the distance from another boid"
    def distance(self, boid):
        distX = self.x - boid.x
        distY = self.y - boid.y
        return math.sqrt(distX * distX + distY * distY)

    "Move closer to a set of boids"
    def moveCloser(self, boids):
        if len(boids) < 1: return

        # calculate the average distances from the other boids
        avgX = 0
        avgY = 0
        for boid in boids:
            if boid.x == self.x and boid.y == self.y:
                continue

            avgX += (self.x - boid.x)
            avgY += (self.y - boid.y)

        avgX /= len(boids)
        avgY /= len(boids)

        # set our velocity towards the others

        self.velocityX -= (avgX / 100)
        self.velocityY -= (avgY / 100)

    "Move with a set of boids"
    def moveWith(self, boids):
        if len(boids) < 1: return
        # calculate the average velocities of the other boids
        avgX = 0
        avgY = 0

        for boid in boids:
            avgX += boid.velocityX
            avgY += boid.velocityY

        avgX /= len(boids)
        avgY /= len(boids)

        # set our velocity towards the others
        self.velocityX += (avgX / 40)
        self.velocityY += (avgY / 40)

    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        if len(boids) < 1: return

        distanceX = 0
        distanceY = 0
        numClose = 0

        for boid in boids:
            distance = self.distance(boid)
            if  distance < minDistance:
                numClose += 1
                xdiff = (self.x - boid.x)
                ydiff = (self.y - boid.y)

                if xdiff >= 0: xdiff = math.sqrt(minDistance) - xdiff
                elif xdiff < 0: xdiff = -math.sqrt(minDistance) - xdiff

                if ydiff >= 0: ydiff = math.sqrt(minDistance) - ydiff
                elif ydiff < 0: ydiff = -math.sqrt(minDistance) - ydiff

                distanceX += xdiff
                distanceY += ydiff

        if numClose == 0:
            return

        self.velocityX -= distanceX / 5
        self.velocityY -= distanceY / 5

    "Perform actual movement based on our velocity"
    def move(self):
        if abs(self.velocityX) > self.velocity_max or abs(self.velocityY) > self.velocity_max:
            scaleFactor = self.velocity_max / max(abs(self.velocityX), abs(self.velocityY))
            self.velocityX *= scaleFactor
            self.velocityY *= scaleFactor

        self.x += self.velocityX
        self.y += self.velocityY

screen = pygame.display.set_mode(size)

# ball = pygame.image.load("ball.png")
ball = pygame.image.load("bee.png")
ballrect = ball.get_rect()

# generate random walls
sizeX = 50
sizeY = 200
for i in range (7):
    a = random.randint(3, width/100)
    b = random.randint(0, height/100)
    walls.append(Wall(a*100, sizeX + a*100, b*100, sizeY + b*100))
for i in range (7):
    a = random.randint(0, width/100)
    b = random.randint(3, height/100)
    walls.append(Wall(a*100, sizeY + a*100, b*100, sizeX + b*100))

# generate borders
walls.append(Wall(0, width,0, border))                  # top
walls.append(Wall(0, width, height - border, height))   # bottom
walls.append(Wall(0, border, 0, height))                # left
walls.append(Wall(width - border, width, 0, height))    # right

# create and draw flower
for i in range(numFlowers):
    flower = Boid(random.randint(0, width), random.randint(0, height), 65, 65, 0)
    if not flower.is_on_wall(walls):
        flowers.append(flower)


# create player
player = Boid(100,100,80,59, 6)
player_image = pygame.image.load("queen.png")
ballrect_player = player_image.get_rect()
player_rect = pygame.Rect(ballrect_player)

goal = Wall(100,200,100,200)

# create boids at random positions
for i in range(numBoids):
    boid = Boid(random.randint(0, width), random.randint(0, height), 50, 37, 4)
    if not boid.is_on_wall(walls):
        boids.append(boid)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # wall collision for the player
    if player.is_on_wall(walls):
        player.velocityX = -player.velocityX
        player.velocityY = -player.velocityY
        while player.is_on_wall(walls):
            player.move()

    for boid in boids:
        if boid.state == "moving":
            closeBoids = []
            for otherBoid in boids:
                if otherBoid == boid: continue
                distance = boid.distance(otherBoid)
                if distance < 100:
                    closeBoids.append(otherBoid)

            boid.moveCloser(closeBoids)
            boid.moveWith(closeBoids)
            boid.moveAway(closeBoids, 20)

            # detect wall collision
            if boid.is_on_wall(walls):
                boid.velocityX = -boid.velocityX * 100;
                boid.velocityY = -boid.velocityY * 100;
                while boid.is_on_wall(walls):
                    boid.move()

            # run after the player
            distance_to_player = boid.distance(player)
            players = []
            players.append(player);
            if distance_to_player < 200:
                boid.moveCloser(players)

            # detect if captured
            goals = [goal]
            if boid.is_on_wall(goals):
                boid.state = "captured"

            # detect flowers
            for flower in flowers:
                if boid.distance(flower) < 10:
                    boid.state = "eating"

        if boid.state == "captured":
            boid_goal = Boid(120 + random.randint(0, 20),150 + random.randint(0, 20),10,10,0)
            boid_goals = [boid_goal]
            boid.moveCloser(boid_goals)
            boid.moveWith(boid_goals)
            boid.moveAway(boid_goals, 5)

        if boid.state == "eating":
            for flower in flowers:
                if boid.distance(flower) < 10:
                    boid.velocityX= boid.velocityX/5;
                    boid.velocityY= boid.velocityY/5;
                    boid.moveCloser([flower])
                    boid.moveAway([flower], 1)
            if boid.distance(player) < 30:
                for i in range (0,20):
                    boid.moveCloser([player])
                boid.state = "moving"




        boid.move()


    player.move()

    screen.fill(white)

    # draw walls
    for wall in walls:
        pygame.draw.rect(screen,black,(wall.x1, wall.y1, wall.x2 - wall.x1, wall.y2 - wall.y1))

    # draw goal
    goal_image = pygame.image.load('beehive.png')
    screen.blit(goal_image, (50,50))

    #draw food
    for flower in flowers:
        flower_image = pygame.image.load('flower.png')
        screen.blit(flower_image, (flower.x - + flower.width/4 ,flower.y - + flower.width/4))

    #draw the player
    player_rect.x = player.x
    player_rect.y = player.y
    screen.blit(player_image, player_rect)


    # draw the boids
    for boid in boids:
        boidRect = pygame.Rect(ballrect)
        boidRect.x = boid.x
        boidRect.y = boid.y
        screen.blit(ball, boidRect)
    pygame.display.flip()
    pygame.time.delay(20)

    for event in pygame.event.get():
        if event.type==KEYDOWN :
            if event.key == 122: #up
                player.velocityX = 0
                player.velocityY = -player.velocity_max
            if event.key == 113: #left
                player.velocityY = 0
                player.velocityX = -player.velocity_max
            if event.key == 100: #right
                player.velocityY = 0
                player.velocityX = player.velocity_max
            if event.key == 115: #down
                player.velocityX = 0
                player.velocityY = player.velocity_max
            if event.key == 27:
                pygame.quit()
                sys.exit()
