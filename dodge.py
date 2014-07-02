import EdgeLaser
import time
import random
import datetime

MAX_X = 500
MAX_Y = 300

START_LIVES = 3


class GameObject(object):
    def __init__(self, x, y, width, length, color=EdgeLaser.LaserColor.LIME):
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.color = color
        self.corners = []

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self):
        p2_x = self.x + self.length
        p2_y = self.y + self.width
        self.corners = [self.x, self.y, p2_x, p2_y]

    def intersect(self, obj):
        hInter = False
        vInter = False

        if not (min(self.x, self.x+self.length) > max(obj.x,obj.x+obj.length) or \
            max(self.x, self.x+self.length) < min(obj.x,obj.x+obj.length)):
            hInter = True

        if not (min(self.y, self.y+self.width) > max(obj.y,obj.y+obj.width) or \
            max(self.y, self.y+self.width) < min(obj.y,obj.y+obj.width)):
            vInter = True

        return vInter and hInter

    def outOfFrame(self):
        if self.x + self.length < 0:
            return True


class Player(GameObject):
    def __init__(self, x, y, width, length, color):
        GameObject.__init__(self, x, y, width, length, color)
        self.score = 0
        self.alive = True

    def move(self, dx, dy):
        #make sure player remain in the field
        self.x = min(max(self.x + dx, 0), MAX_X - 1 - self.length)
        self.y = min(max(self.y + dy, 0), MAX_Y - 1 - self.width)

    def bump(self, player):
        center1 = self.x+self.length/2, self.y+self.width/2
        center2 = player.x+player.length/2, player.y+player.width/2

        player.move(center2[0]-center1[0], center2[1]-center1[1])
        self.move(center1[0]-center2[0], center1[1]-center2[1])

    def intersect(self, obj):
        if self.alive:
            return GameObject.intersect(self, obj)

    def crash(self):
        #self.score -= 1
        self.alive = False


class Dodge(object):
    MAX_CARS = 5
    CAR_SPEED = 5
    MIN_WAIT = 500
    MAX_WAIT = 2000
    WIDTH = 30
    LENGTH = 40

    def __init__(self):
        self.cars = []
        self.timer = None
        self.lastCreation = None
        self.crashTime = None

    def setTimer(self):
        self.timer = datetime.timedelta(milliseconds=random.randint(Dodge.MIN_WAIT, Dodge.MAX_WAIT))

    def createCar(self):
        if len(self.cars) < self.MAX_CARS:
            car = GameObject(MAX_X - 1, random.randint(0, MAX_Y-1-Dodge.WIDTH), Dodge.WIDTH, Dodge.LENGTH)
            self.cars.append(car)
            self.lastCreation = datetime.datetime.now()
            self.setTimer()

    def manageCars(self, animated):
        if self.timer is None:
            self.setTimer()

        if self.lastCreation is None:
            self.createCar()
        elif datetime.datetime.now() > self.lastCreation + self.timer:
            self.createCar()

        for car in self.cars:
            if car.outOfFrame():
                self.cars.remove(car)
            else:
                if animated:
                    car.move(-Dodge.CAR_SPEED, 0)
                car.draw()


if __name__ == "__main__":
    game = EdgeLaser.LaserGame('Dodge')

    game.setResolution(500).setDefaultColor(EdgeLaser.LaserColor.LIME)
    game.setFrameRate(20)
    font = EdgeLaser.LaserFont('lcd.elfc')

    reset = True

    while True:
        while game.isStopped():
            game.receiveServerCommands()
            time.sleep(0.5)

        player1 = Player(100, 70, 30, 40, EdgeLaser.LaserColor.BLUE)
        player2 = Player(100, 170, 30, 40, EdgeLaser.LaserColor.RED)
        dodge = Dodge()
        reset = False

        while not game.isStopped():
            if reset:
                player1.move(100 - player1.x, 70 - player1.y)
                player2.move(100 - player2.x, 170 - player2.y)
                player1.alive = True
                player2.alive = True
                dodge = Dodge()
                reset = False

            game.newFrame()

            commands = game.receiveServerCommands()

            # for cmd in commands:
            if game.player1_keys and player1.alive:
                if game.player1_keys.yp:
                    player1.move(0, -5)
                if game.player1_keys.xn:
                    player1.move(-5, 0)
                if game.player1_keys.yn:
                    player1.move(0, 5)
                if game.player1_keys.xp:
                    player1.move(5, 0)

            if game.player2_keys and player2.alive:
                if game.player2_keys.yp:
                    player2.move(0, -5)
                if game.player2_keys.xn:
                    player2.move(-5, 0)
                if game.player2_keys.yn:
                    player2.move(0, 5)
                if game.player2_keys.xp:
                    player2.move(5, 0)

            if player1.intersect(player2):
                player1.bump(player2)

            for car in dodge.cars:
                if player1.intersect(car):
                    player1.crash()
                    dodge.crashTime = datetime.datetime.now()
                    player2.score += 1
                if player2.intersect(car):
                    player2.crash()
                    dodge.crashTime = datetime.datetime.now()
                    player1.score += 1
                game.addRectangle(*car.corners)

            dodge.manageCars(player1.alive and player2.alive)
            player1.draw()
            player2.draw()
            game.addRectangle(*player1.corners, color=player1.color)
            game.addRectangle(*player2.corners, color=player2.color)

            game.addLine(0, 0, MAX_X-1, 0)
            game.addLine(0, MAX_Y-1, MAX_X-1, MAX_Y-1)

            if not player1.alive or not player2.alive:
                if datetime.datetime.now() > dodge.crashTime + datetime.timedelta(seconds=3):
                    #print("Player 1 : %s, Player2 : %s" % (player1.score, player2.score))
                    reset = True

            font.render(game, str(player1.score), 10, 10, player1.color, 2)
            font.render(game, str(player2.score), 10, MAX_Y - 30, player2.color, 2)

            game.refresh()
            game.endFrame()