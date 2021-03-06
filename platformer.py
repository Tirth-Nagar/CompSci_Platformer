# Author: Tirth Nagar and Arjan
# Date: January 16th, 2022
# File Name: platformer.py
# Description: Simple platformer game made for computer science class

# Import statements
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

# Pygame Initializations
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 165

# Define screen dimensions
screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Forlorn")

# Define Font
font = pygame.font.SysFont("Bauhaus 93", 70)
font_score = pygame.font.SysFont("Bauhaus 93", 30)
font_title = pygame.font.SysFont("Times New Roman", 90)
font_text_title = pygame.font.SysFont("Times New Roman", 75)
font_text = pygame.font.SysFont("Bauhaus 93", 75)

# Define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 10
score = 0

# Define Colours
white = (255, 255, 255)
blue = (0, 0, 255)

# Load images
moon_img = pygame.image.load("images/Moon.png")
moon_img = pygame.transform.scale(moon_img, (500, 500))

bg_img = pygame.image.load("images/Night_Sky.png")
restart_img = pygame.image.load("images/restart_btn.png")
start_img = pygame.image.load("images/start_btn.png")

exit_img = pygame.image.load("images/exit_btn.png")

controls_img = pygame.image.load("images/controls_btn.png")
controls_img = pygame.transform.scale(controls_img, (279, 126))

controls_background = pygame.image.load("images/Controls_BG.png")

back_img = pygame.image.load("images/back.png")
back_img = pygame.transform.scale(back_img, (150, 75))

# Load Sounds
lobby_music = pygame.mixer.Sound("sounds/lobby_music.mp3")
lobby_music.set_volume(0.5)

coin_fx = pygame.mixer.Sound("sounds/coin.wav")
coin_fx.set_volume(1)

jump_fx = pygame.mixer.Sound("sounds/jump.wav")
jump_fx.set_volume(1)

game_over_fx = pygame.mixer.Sound("sounds/game_over.wav")
game_over_fx.set_volume(1)

# Function to play music


def play_music(level):
    game_music = ["lvl_0.mp3", "lvl_1.mp3", "lvl_2.mp3", "lvl_3.mp3",
                  "lvl_4.mp3", "lvl_5.mp3", "lvl_6.mp3", "lvl_7.mp3","lvl_8.mp3","lvl_9.mp3","lvl_10.mp3"]
    if level <= 10:
        pygame.mixer.music.load("sounds/" + game_music[level])
        pygame.mixer.music.play(loops=-1)
    elif level == 11:
        pygame.mixer.music.load("sounds/end_music.mp3")
        pygame.mixer.music.play(loops=-1)

# Function to draw text on screen


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to reset level


def reset_level(level):
    Player.reset(100, screen_height-130)
    enemy_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    # Load in level data and create world
    if path.exists(f"levels/{level}_level_data"):
        pickle_in = open(f"levels/{level}_level_data", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

# Function to draw gridlines to **debug**


def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255),
                         (0, line*tile_size), (screen_width, line*tile_size))
        pygame.draw.line(screen, (255, 255, 255),
                         (line*tile_size, 0), (line*tile_size, screen_height))

# Button class to simply draw buttons and check if they are clicked


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # Get mouse position
        X_pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(X_pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                # print("Clicked")
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw the button
        screen.blit(self.image, self.rect)

        return action

# Player class to define player properties and movement and check for collisions


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 5
        collison_threshold = 20

        if game_over == 0:
            # Get keypresses
            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True

            if keys[pygame.K_SPACE] == False:
                self.jumped = False

            if keys[K_LEFT]:
                dx = -5
                self.counter += 1
                self.direction = -1
            if keys[K_RIGHT]:
                dx = 5
                self.counter += 1
                self.direction = 1
            if keys[K_LEFT] == False and keys[K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Handle Animations
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10

            dy += self.vel_y

            # Check for Collisions with the ground and ceiling
            self.in_air = True
            for tile in world.tile_list:
                # Check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Check for collision in the y-direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below the ground (When jumping)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Check if above the ground (When falling)
                    elif self.vel_y > 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Check for collision with the enemies
            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over = -1
                game_over_fx.play()

            # Check for collision with the lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # Check for collision with the exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # Check for collision with platforms
            for platform in platform_group:
                # Collision in x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # Collision in y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below the platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < collison_threshold:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # Check if above the platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < collison_threshold:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # Move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # Update player position
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text("Game Over", font, white,
                      (screen_width//2)-140, screen_height//2)
            if self.rect.y > 50:
                self.rect.y -= 5

        # Draw player on the screen
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    # Reset Player
    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f"images/guy{num}.png")
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("images/ghost.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

# World class to draw the world and


class World():
    def __init__(self, data):
        self.tile_list = []

        # Load images
        dirt_img = pygame.image.load("images/dirt.png")
        grass_img = pygame.image.load("images/grass.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(
                        dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count*tile_size
                    img_rect.y = row_count*tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(
                        grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count*tile_size
                    img_rect.y = row_count*tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count*tile_size, row_count*tile_size+15)
                    enemy_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count*tile_size,
                                        row_count*tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count*tile_size,
                                        row_count*tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count*tile_size, row_count *
                                tile_size + (tile_size//2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count*tile_size + (tile_size//2),
                                row_count*tile_size + (tile_size//2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count*tile_size, row_count *
                                tile_size - (tile_size//2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# Enemy class to draw the enemies


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/enemy.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# Platform class to draw the platforms and control their movement


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("images/platform.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# Lava class to draw the lava


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/lava.png")
        self.image = pygame.transform.scale(
            self.image, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Coin class to draw the coins


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/coin.png")
        self.image = pygame.transform.scale(
            self.image, (tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Exit class to draw the exits


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/exit.png")
        self.image = pygame.transform.scale(
            self.image, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Create player instance and starting position
Player = Player(100, screen_height-130)

# Add sprites to groups
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Create dummy coin for showing the player how many coins they have
score_coin = Coin(125//2, tile_size//2)
coin_group.add(score_coin)

# Load in level data and create world
if path.exists(f"levels/{level}_level_data"):
    pickle_in = open(f"levels/{level}_level_data", "rb")
    world_data = pickle.load(pickle_in)

# Create the world using the world class
world = World(world_data)

# Create Buttons
restart_button = Button(screen_width//2-50, screen_height//2 + 100, restart_img)
start_button = Button(screen_width//2-350, screen_height//2+75, start_img)
exit_button = Button(screen_width//2-115, screen_height//2+250, exit_img)
controls_button = Button(screen_width//2+75, screen_height//2+75, controls_img)
back_button = Button(screen_width//2-475, 50, back_img)

controls = False
run = True

# Game Loop
while run:
    clock.tick(fps)
    # Show background
    screen.blit(bg_img, (0, 0))
    screen.blit(moon_img, (-50, -25))

    if main_menu == True:
        lobby_music.play(-1, fade_ms=5000)
        draw_text("Forlorn", font_title, white,
                  screen_width//2-125, screen_height//2-100)
        if exit_button.draw():
            run = False
        if start_button.draw():
            lobby_music.stop()
            main_menu = False
            play_music(level)
        if controls_button.draw():
            main_menu = False
            controls = True

    elif controls == True:
        # Display controls
        screen.fill(white)
        screen.blit(controls_background, (0, 0))
        draw_text("Controls", font_title, white, screen_width//2-175, 50)
        draw_text("Move Left:", font_text_title, white, 75, 225)
        draw_text("[Left Arrow]", font_text, white, 525, 225)
        draw_text("Move Right:", font_text_title, white, 75, 400)
        draw_text("[Right Arrow]", font_text, white, 525, 400)
        draw_text("Jump:", font_text_title, white, 75, 575)
        draw_text("[Spacebar]", font_text, white, 525, 575)
        if back_button.draw():
            controls = False
            main_menu = True
        pygame.display.update()

    else:
        world.draw()

        if level <= 10:
            draw_text("Level " + str(level), font_score,
                  white, screen_width//2-40, 10)
        elif level >= 11:
            draw_text("Congratulations!", font_score,
                  white, screen_width//2-100, 10)
        
        if game_over == 0:
            enemy_group.update()
            platform_group.update()
            # Check if a coin has been collected
            if pygame.sprite.spritecollide(Player, coin_group, True):
                score += 1  # Update Score
                coin_fx.play()
            draw_text("X" + str(score), font_score, white, tile_size+30, 10)
            # print(score) **Debugging**

        # Draw all sprites on the screen
        platform_group.draw(screen)
        enemy_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = Player.update(game_over)

        # If player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # If player has won
        if game_over == 1:
            # reset game and go to the next level
            level += 1
            # print(level) # Debugging
            if level <= max_levels:
                play_music(level)
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                play_music(level)
                draw_text("YOU WIN!", font, white,
                          (screen_width//2)-140, screen_height//2)

                if restart_button.draw():
                    level = 0
                    play_music(level)
                    # reset game from scratch
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

        # draw_grid() **debugging**

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
