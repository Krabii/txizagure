# Initialize pygame library
import os
import pygame
from collections import namedtuple
from math import isclose
from random import randint, choices
from pygame.locals import *


VERSION = "0.1"
SCREEN_DIMENSIONS = [1280, 720]
ABS_TOL = 18
LIMIT = 8


pygame.font.init()
food = namedtuple('Food', 'name unicode kakagure txizagure gasak')
janariak = {
    'sandia': food('sandia', '1F349', 1, 3, 0),
    'berakatza': food('berakatza', '1F9C4', 2, 1, 3),
    'perrito_caliente': food('Hot Dog', '1F32D', 3, 1, 3),
    'kokakola': food("Coca Cola", '1F9CB', 0, 3, 0),
    'pizza': food('pizza', '1F355', 2, 0, 1),
    'pastela': food('pastela', '1F370', 3, 0, 1),
    'sushi': food('sushi', '1F363', 1, 1, 2),
    'spaghetti': food('spaghetti', '1F35D', 2, 0, 2),
    'kafe': food('kafe', '2615', 1, 3, 2),
    'te': food('te', '1FAD6', 0, 3, 0),
    'esnea': food('esnea', '1F95B', 0, 2, 1),
    'yogur': food('yogur', '1FAD9', 1, 1, 1),
    'marrubia': food('marrubi', '1F353', 1, 1, 0),
    'melokotoi': food('melokotoi', '1F351', 1, 1, 0),
    'taco': food('taco','1F32F', 1, 0, 3),
    'ramen': food('ramen', '1F35C', 1, 1, 0),
    'perretxiko': food('perretxiko', '1F344', 0, 0, 0),
    'skull': food('skull', '1F480', 0, 0, 0)
}
names = list(janariak.keys())


def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join("assets", name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except FileNotFoundError:
        print(f"Cannot load image: {fullname}")
        raise SystemExit
    return image, image.get_rect()


class AttackObject(pygame.sprite.Sprite):
    def __init__(self, type):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.type = type
        self.speed = 30
        self.moving = False
        self.direction = 'right'
        if self.type == "kakagure":
            self.image, self.rect = load_png(f"openmoji-72x72-color/1F4A9.png")
        if self.type == "txizagure":
            self.image, self.rect = load_png(f"openmoji-72x72-color/1F4A6.png")
        if self.type == "gasak":
            self.image, self.rect = load_png(f"openmoji-72x72-color/1F4A8.png")
        self.reinit()

    def reinit(self):
        self.rect.y = -300 # self.atacante.rect.y
        self.rect.x = -300 # self.atacante.rect.x + 20
        self.moving = False
        self.direction = 'right'

    def shoot(self, pos_x, pos_y, other_x):
        self.rect.y = pos_y
        self.rect.x = pos_x
        self.moving = True
        if other_x > pos_x:
            self.direction = 'right'
        else:
            self.direction = 'left'
    
    def move(self, dt):
        if self.direction == 'right':
            self.rect.x += self.speed * dt
        else:
            self.rect.x -= self.speed * dt
        if self.rect.x > SCREEN_DIMENSIONS[0] or self.rect.x < -30:
            self.reinit()



class FallingObject(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.reinit()

    def reinit(self):
        weights = [0.1 if name in ["perretxiko", "skull"] else 0.9 for name in names]
        self.name = choices(names, weights=weights)[0]
        self.food = janariak[self.name]
        self.unicode = janariak[self.name].unicode
        self.image, self.rect = load_png(f"openmoji-72x72-color/{self.unicode}.png")
        self.rect.y = -50
        self.rect.x = randint(0, SCREEN_DIMENSIONS[0])
        self.speed = randint(1, 4)

    def fall(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_DIMENSIONS[1]:
            self.reinit()


class Player(pygame.sprite.Sprite):
    """The Player class. A player can move right and left and also jump.
    Returns: Player object
    Functions:assets/openmoji-72x72-color/1F924.png
    Attributes: color, radius"""

    def __init__(self, side):
        pygame.sprite.Sprite.__init__(self)
        if side == 'left':
            self.image, self.rect = load_png("openmoji-72x72-color/1F924.png")
        elif side == 'right':
            self.image, self.rect = load_png("openmoji-72x72-color/1F437.png")
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.side = side
        self.life = 40
        self.kakagure = 0
        self.txizagure = 0
        self.gasak = 0
        self.reinit()
        self.kaka = AttackObject('kakagure')
        self.txiz = AttackObject('txizagure')
        self.gas = AttackObject('gasak')

    def reinit(self):
        if self.side == "left":
            self.rect.bottomleft = self.area.bottomleft
        elif self.side == "right":
            self.rect.bottomright = self.area.bottomright

    def move(self, step):
        self.rect.x += step

    def eat(self, obj: FallingObject, other_player):
        if obj.food.name == 'skull':
            self.life -= 5
        if obj.food.name == "perretxiko":
            # self.image = "openmoji-72x72-color/1F635-200D-1F4AB.png")
            pass
        self.kakagure += obj.food.kakagure
        self.txizagure += obj.food.txizagure
        self.gasak += obj.food.gasak


def main():

    pygame.init()
    font = pygame.font.Font(None, 32)
    # Set up the drawing window
    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    pygame.display.set_caption('KakaPedoTxiz')

    # Fill the background with white
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    dt = 0

    # Initialise players
    global player1
    global player2
    player1 = Player("left")
    player2 = Player("right")
    objs = [FallingObject() for _ in range(18)]

    # Initialise sprites
    playersprites = pygame.sprite.RenderPlain((player1, player2))
    object_sprites = pygame.sprite.RenderPlain([x for x in objs])
    att_obj_sprites = pygame.sprite.RenderPlain([player1.kaka, player2.kaka, player1.txiz, player2.txiz, player1.gas, player2.gas])

    # colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock
    clock = pygame.time.Clock()

    # Run until the user asks to quit
    running = True
    while running:
        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000.0

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("KAKA TXIZA TA PUZKERRA!!", 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        background.blit(text, textpos)
        background.blit(font.render(f"Bizitza: {player1.life:4} ", True, black, white), (100, 60))
        background.blit(font.render(f"Kakagure: {player1.kakagure:4} ", True, black, white), (100, 100))
        background.blit(font.render(f"Txizagure: {player1.txizagure:4} ", True, black, white), (100, 140))
        background.blit(font.render(f"Gasak: {player1.gasak:4} ", True, black, white), (100, 180))
        background.blit(font.render(f"Bizitza: {player2.life:4} ", True, black, white), (SCREEN_DIMENSIONS[0] - 200, 60))
        background.blit(font.render(f"Kakagure: {player2.kakagure:4} ", True, black, white), (SCREEN_DIMENSIONS[0] - 200, 100))
        background.blit(font.render(f"Txizagure: {player2.txizagure:4} ", True, black, white), (SCREEN_DIMENSIONS[0] - 200, 140))
        background.blit(font.render(f"Gasak: {player2.gasak:4} ", True, black, white), (SCREEN_DIMENSIONS[0] - 200, 180))

        # Read keystrokes
        keys = pygame.key.get_pressed()
        if keys[K_a]:
            player1.move(-(300 * dt))
        if keys[K_d]:
            player1.move(+(300 * dt))
        if keys[K_LEFT]:
            player2.move(-(300 * dt))
        if keys[K_RIGHT]:
            player2.move(+(300 * dt))

        # Keep Falling
        for obj in objs:
            obj.fall()
            player1.kaka.move(dt)
            player1.txiz.move(dt)
            player1.gas.move(dt)
            player2.kaka.move(dt)
            player2.txiz.move(dt)
            player2.gas.move(dt)
            # Player eats falling object
            if isclose(player1.rect.x, obj.rect.x, abs_tol=ABS_TOL) \
                    and isclose(player1.rect.y, obj.rect.y, abs_tol=ABS_TOL):
                player1.eat(obj, player2)
                obj.reinit()
            if isclose(player2.rect.x, obj.rect.x, abs_tol=ABS_TOL) \
                    and isclose(player2.rect.y, obj.rect.y, abs_tol=ABS_TOL):
                player2.eat(obj, player1)
                obj.reinit()
            if player1.kakagure >= LIMIT:
                player1.kakagure = 0
                player1.kaka.shoot(player1.rect.x, player1.rect.y, player2.rect.x)
            if player1.txizagure >= LIMIT:
                player1.txizagure = 0
                player1.txiz.shoot(player1.rect.x, player1.rect.y, player2.rect.x)
            if player1.gasak >= LIMIT:
                player1.gasak = 0
                player1.gas.shoot(player1.rect.x, player1.rect.y, player2.rect.x)
            if player2.kakagure >= LIMIT:
                player2.kakagure = 0
                player2.kaka.shoot(player2.rect.x, player2.rect.y, player1.rect.x)
            if player2.txizagure >= LIMIT:
                player2.txizagure = 0
                player2.txiz.shoot(player2.rect.x, player2.rect.y, player1.rect.x)
            if player2.gasak >= LIMIT:
                player2.gasak = 0
                player2.gas.shoot(player2.rect.x, player2.rect.y, player1.rect.x)
            if isclose(player1.kaka.rect.x, player2.rect.x, abs_tol=4):
                print("KAKAKAKAKAKA")
                player1.kaka.reinit()
                player2.life -= 3
            if isclose(player1.txiz.rect.x, player2.rect.x, abs_tol=4):
                print("TXIZA")
                player1.txiz.reinit()
                player2.life -= 3
            if isclose(player1.gas.rect.x, player2.rect.x, abs_tol=4):
                print("PUZKERRA")
                player1.gas.reinit()
                player2.life -= 3
            if isclose(player2.kaka.rect.x, player1.rect.x, abs_tol=4):
                print("KAKAKAKAKAKA")
                player2.kaka.reinit()
                player1.life -= 3
            if isclose(player2.txiz.rect.x, player1.rect.x, abs_tol=4):
                print("TXIZA")
                player2.txiz.reinit()
                player1.life -= 3
            if isclose(player2.gas.rect.x, player1.rect.x, abs_tol=4):
                print("PUZKERRA")
                player2.gas.reinit()
                player1.life -= 3
            if player1.life <=0:
                background.blit(font.render(f"GAME OVER: PLAYER 2 IRABAZLE!!!", True, black, white), (600, 350))
            if player2.life <=0:
                background.blit(font.render(f"GAME OVER: PLAYER 1 IRABAZLE!!!", True, black, white), (600, 350))


        # Flip the display
        screen.blit(background, (0, 0))

        playersprites.update()
        object_sprites.update()
        att_obj_sprites.update()

        playersprites.draw(screen)
        object_sprites.draw(screen)
        att_obj_sprites.draw(screen)
        pygame.display.flip()

    # Done! Time to quit.
    pygame.quit()


if __name__ == "__main__":
    main()
