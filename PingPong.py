import pygame
import time
import math
import random
import socket
import re
from threading import Thread
from pygame.locals import *


outData = 0 # Evil Evil Global Variable
_debug = 1

# UDP packet receiver
class UDPRecv:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 20321))

    def __init__(self):
        self.lastresult = 0

    def getData(self):
        global outData
        self.check = 0
        while True:
            self.data, self.address = self.sock.recvfrom(1024)
            self.m = re.search('ResultCode (.)', self.data)
            if self.m:
                self.a = self.m.group(1)
                outData = int(self.a)
                if outData != 0 and self.check == 0:
                    self.check = 1
                elif outData != 0 and self.check == 1:
                    outData = 0
                else:
                    self.check = 0
                    outData = 0
                print outData

    def getCommand(self):
        global outData, _debug
        while True:
            # Get data from socket
            self.data, self.address = self.sock.recvfrom(1024)

            # Look for feedback
            result = re.search('ResultCode (.)', self.data)
            if result:
                result = int(result.group(1))
                if _debug:
                    print type(result)
                    print "*** Result detected"
                    print 'result: %d' % result
                    # print type(self.lastfeedback)
                    print 'lastresult: %d' % self.lastresult
                    print ''

                 # Check if a command should be sent
                if result and self.lastresult==0: # the first time result code appears
                    outData = result
                    if _debug:
                        print '================================='
                        print 'isFist checked'
                        print 'outData: %d' % outData

                # Update last result
                self.lastresult = result

class Game:
    def isCollision(self, x1, y1, x2, y2, bsize):
        if x1 >= x2  and x1 <= x2 + bsize:
            if y1 >= y2 and y1 <= y2 + bsize:
                return True
        return False
class App:

    windowWidth = 800
    windowHeight = 600
    player = 0
    ball = 0
    angle = random.randint(30,60) # Initialize position and path
    direction = random.randint(0,1)
    score = 0
    highestScore = 0
    highestScoreText = 0
    myfont = 0
    text = 0
    timer = 0
    timerText = 0
    timerStep = 20/1000.0

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self.player = Bar()
        self.ball = Ball()
        self.game = Game()
        self.udp = UDPRecv()
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)
        pygame.display.set_caption('Euphoria')
        self._running = True
        self._image_surf = pygame.image.load("bar.png").convert()
        self._ball_surf = pygame.image.load("ball.png").convert()
        self.myfont = pygame.font.SysFont("None", 30)

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):

        self.text = self.myfont.render("Score: " + str(self.score), 0, (255,255,255))
        self.highestScoreText = self.myfont.render("Highest Score: " + str(self.highestScore), 0, (255,255,255))
        self.timerText = self.myfont.render("Time elapsed: " + str(self.timer) + " " + "seconds", 0, (255,255,255))
        # Collision with player
        for i in range(-4, 4, 1):
            if self.game.isCollision(self.ball.x,self.ball.y,self.player.x + i*39, self.player.y - 40, 39) and self.direction == 2: # Collision going right -> left
                self.direction = 1
                self.score += 1
                #self.ball.step += 2

            if self.game.isCollision(self.ball.x,self.ball.y,self.player.x + i*39, self.player.y - 40, 39) and self.direction == 3: # Collision going left -> right
                self.direction = 0
                self.score += 1

                #self.ball.step += 2

        if self.ball.y > self.windowHeight + 100: # Losing condition
            self.ball.y = self.windowHeight - 0.5*self.windowHeight
            self.ball.x = random.randint(self.windowWidth/3,self.windowWidth * 2/3)
            self.angle = random.randint(30,60) # Initialize position and path
            self.direction = random.randint(0,1)
            self.score += -1
            #self.ball.step += -2
        self.timer += self.timerStep

        # Left Side Collision Going Up
        if self.ball.x <= 0 and self.direction == 1:
            self.direction = 0
        # Left Side Collision Going Down
        if self.ball.x <= 0 and self.direction == 2:
            self.direction = 3
        # Right Side Collision Going Up
        if self.ball.x >= self.windowWidth-30 and self.direction == 0:
            self.direction = 1
        # Right Side Collision Going Down
        if self.ball.x >= self.windowWidth-30 and self.direction == 3:
            self.direction = 2
        # Top Side Collision Going Left
        if self.ball.y <= 0 and self.direction == 1:
            self.direction = 2
        # Top Side Collision Going Right
        if self.ball.y <= 0 and self.direction == 0:
            self.direction = 3
        # Highest score
        if self.highestScore < self.score:
            self.highestScore = self.score
        # Jokes
        pass

    def on_render(self):
        self._display_surf.fill((0,0,0))
        self._display_surf.blit(self._ball_surf,(self.ball.x, self.ball.y))
        self.player.draw(self._display_surf, self._image_surf )
        self._display_surf.blit(self.text, (self.windowWidth/2 - 120,self.windowHeight*0.1)) # Score
        self._display_surf.blit(self.timerText, (self.windowWidth/2 - 120,self.windowHeight*0.140)) # Timer
        self._display_surf.blit(self.highestScoreText, (self.windowWidth/2,self.windowHeight*0.1)) # High score
        pygame.display.flip()

    def on_cleanup(self):
        self.udp.sock.close()
        pygame.quit()

    def on_execute(self):
        global outData
        if self.on_init() == False:
            self._running = False


        while( self._running ):
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if (keys[K_RIGHT]):
                self.player.moveRight()

            if (keys[K_LEFT]):
                self.player.moveLeft()

            if (keys[K_ESCAPE]):
                self._running = False

            if outData == 2:
                self.player.moveRight()

            if outData == 4:
                self.player.moveLeft()

            if self.ball.y < self.windowHeight + 100:
                self.ball.displacement(self.ball.x,self.ball.y,self.angle, self.direction)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
            self.on_loop()
            self.on_render()

            time.sleep(self.timerStep)

        self.on_cleanup()

class Bar:
    x = App.windowWidth/2
    y = App.windowHeight*0.9
    speed = 50

    def moveRight(self):
        self.x = self.x + self.speed
        if self.x >= App.windowWidth - 4*39:
            self.x = App.windowWidth - 4*39

    def moveLeft(self):
        self.x = self.x - self.speed
        if self.x <= 4*39:
            self.x = 4*39
    def draw(self, surface, image):
        for i in range(-4, 4, 1):
            surface.blit(image,(self.x + i*39, self.y))
class Ball:
    x = App.windowWidth/2
    y = 0.5*App.windowHeight
    step = 10
    def displacement(self, x, y, angle, direction):
        if direction == 0:
            x += math.cos(math.radians(angle)) * self.step
            y -= math.sin(math.radians(angle)) * self.step
        if direction == 1:
            x += -math.cos(math.radians(angle)) * self.step
            y -= math.sin(math.radians(angle)) * self.step
        if direction == 2:
            x += -math.cos(math.radians(angle)) * self.step
            y -= -math.sin(math.radians(angle)) * self.step
        if direction == 3:
            x += math.cos(math.radians(angle)) * self.step
            y -= -math.sin(math.radians(angle)) * self.step
        self.x = x
        self.y = y



if __name__ == "__main__":
    theApp = App()
    udp = UDPRecv()
    t1 = Thread(target=theApp.on_execute)
    t2 = Thread(target=udp.getData)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
