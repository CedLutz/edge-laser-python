import EdgeLaser
import time

game = EdgeLaser.LaserGame('SuperTetris')

game.setResolution(500).setDefaultColor(EdgeLaser.LaserColor.LIME)

coeff = 0

posx = 450

posy = 450

font = EdgeLaser.LaserFont('lcd.elfc')

while game.isStopped():
    game.receiveServerCommands()

i = 1
while not game.isStopped():
    commands = game.receiveServerCommands()

    # for cmd in commands:

    if game.player1_keys:
        if game.player1_keys.yp  :
            posy-=5
        if game.player1_keys.xn :
            posx-=5
        if game.player1_keys.yn :
            posy+=5
        if game.player1_keys.xp :
            posx+=5

    coeff = 0 if coeff > 499 else coeff + 4

    font.render(game, 'EDGEFEST 2014', 20, 40, coeff=3)

    game.addRectangle(250, 400, 550, 450)

    game.refresh()
    time.sleep(0.05)
