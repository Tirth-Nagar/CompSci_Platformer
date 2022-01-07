import pygame
from pygame.locals import *
import pickle
from os import path
pygame.init()

clock = pygame.time.Clock()
fps = 165

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dreamscape")

# Define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 0

# Load images
sun_img = pygame.image.load("images/sun.png")
bg_img = pygame.image.load("images/sky.png")
restart_img = pygame.image.load("images/restart_btn.png")
start_img = pygame.image.load("images/start_btn.png")
exit_img = pygame.image.load("images/exit_btn.png")

def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255),
                         (0, line*tile_size), (screen_width, line*tile_size))
        pygame.draw.line(screen, (255, 255, 255),
                         (line*tile_size, 0), (line*tile_size, screen_height))

class Button():
    def __init__(self,x,y,image):
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


class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self,game_over):

        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # Get keypresses
            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
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
            
            #Check for collision with the enemies  
            if pygame.sprite.spritecollide(self,enemy_group,False):
                game_over = -1
            # Check for collision with the lava
            if pygame.sprite.spritecollide(self,lava_group,False):
                game_over = -1


            # Update player position
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 50:
                self.rect.y -=  5

        # Draw player on the screen
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self,x,y):
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
                if tile == 6:
                    lava = Lava(col_count*tile_size, row_count*tile_size + (tile_size//2))
                    lava_group.add(lava)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


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

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/lava.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


Player = Player(100, screen_height-130)

lava_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Load in level data and create world
if path.exists(f"levels/{level}_level_data"):
    pickle_in = open(f"levels/{level}_level_data", "rb")
    world_data = pickle.load(pickle_in)

world = World(world_data)

# Create Buttons
restart_button = Button(screen_width//2-50, screen_height//2 + 100,restart_img)
start_button = Button(screen_width//2-350, screen_height//2,start_img)
exit_button = Button(screen_width//2+100, screen_height//2,exit_img)

run = True
while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    
    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            enemy_group.update()

        enemy_group.draw(screen)
        lava_group.draw(screen)

        game_over = Player.update(game_over)

        # If player has died
        if game_over == -1:
            if restart_button.draw():
                # print("Restart")
                Player.reset(100,screen_height-130)
                game_over = 0

        # draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
