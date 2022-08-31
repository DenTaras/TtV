# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 17:07:23 2022

@author: Denis
"""
from random import randint
import pygame
import math
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import func


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class Sprite():
    list_draw = []
    list_ships = []
    list_bullets = []


class Ship(Sprite):
    def __init__(self, image_list, shoot_sound, x, y): 
        Sprite().list_draw.append(self)
        Sprite().list_ships.append(self)
        self.image_list = image_list
        self.anim_count = 0
        self.time_count = 0
        self.image = self.image_list[self.anim_count]
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.image_rot = self.image
        self.rect_rot = self.image_rot.get_rect()
        self.angle_front = 0
        self.angle_target = 0
        self.rotation_vel = 3
        self.speed = 0         
        self.speed_up = 0.1  
        self.timer = 0
        

    def move(self):
        anggle_rad = math.radians(self.angle_front)
        x_shift = math.sin(anggle_rad)
        y_shift = math.cos(anggle_rad)
        self.x -= x_shift * self.speed
        self.y -= y_shift * self.speed
     
    def rot(self):
        self.image_rot = pygame.transform.rotate(self.image, self.angle_front)
        self.rect_rot =  self.image_rot.get_rect(center=self.image.get_rect(topleft=(self.x, self.y)).center)
        
    def anim_image(self):
        if self.anim_count > len(self.image_list) -2:
            self.anim_count = 0
        else:
            self.anim_count += 1
        self.image = self.image_list[self.anim_count]
        
    def update(self):
        if self.speed < 4:
            self.speed += self.speed_up
        
        if self.angle_front > self.angle_target:
            self.angle_front -= self.rotation_vel
        else:
            self.angle_front += self.rotation_vel
        #возвращение в границы
        delta = 100
        if self.x > WIDTH + delta:
            self.x = 0 - delta
        if self.x < 0 - delta:
            self.x = WIDTH + delta
        
        if self.y > HEIGHT + delta:
            self.y = 0 - delta
        if self.y < 0 - delta:
            self.y = HEIGHT + delta
        
        # таймер
        self.timer += 1
        if self.timer == 100:
            self.angle_target = randint(0, 360)
            self.timer = 0
        
            
        self.rot()
        self.move()
        
    def draw(self, screen):
        if self.time_count == 10:
            self.anim_image()
            self.time_count = 0
        else:
            self.time_count += 1
        screen.blit(self.image_rot, self.rect_rot.topleft)
 
    def shoot(self):
        Bullet(bullet_imag, self.rect_rot.centerx, self.rect_rot.centery, self.angle_front, self.speed)
        shoot_sound.play()

        
class Player_Ship(Ship):
    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            self.speed += self.speed_up
        if key[pygame.K_s]:
            self.speed -= self.speed_up
        
        
        if key[pygame.K_a]:
            self.angle_front += self.rotation_vel
        if key[pygame.K_d]:
            self.angle_front -= self.rotation_vel    
        
        self.rot()
        self.move()
    
#--------------------------------
class Bullet(Sprite):
    def __init__(self, bullet_imag, x, y, angle_front, speed):
        Sprite().list_bullets.append(self)
        Sprite().list_draw.append(self)
        self.image = bullet_imag
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.angle_front = angle_front
        self.speed = 10 + speed
        self.hp = 80



    def move(self):
        anggle_rad = math.radians(self.angle_front)
        x_shift = math.sin(anggle_rad)
        y_shift = math.cos(anggle_rad)
        self.x -= x_shift * self.speed
        self.y -= y_shift * self.speed
        self.hp -= 1
        
        
    def kill(self):
        Sprite().list_bullets.remove(self)
        Sprite().list_draw.remove(self)

    def update(self):
        self.move()
        if self.hp < 0:
            self.kill()
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))




class Camera():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
    
    def draw(self):
        for sprite in Sprite().list_draw:
            self.display_surface.blit(sprite.image, sprite.rect)



############################################################################################
WIDTH = 1920  # ширина игрового окна
HEIGHT = 1080 # высота игрового окна
FPS = 60 # частота кадров в секунду
WHITE = (255,255,255)
BLACK = (0,0,0)
#--------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("through the void")  
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')
#--------------------------------
# Папки с файлами
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'snd')
#--------------------------------
shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'laser-gun-single-shot.mp3'))
#--------------------------------
background = func.scale_image(pygame.image.load(os.path.join(img_folder, 'cosmos.jpg')), 1)
background_rect = background.get_rect()
#--------------------------------
ship_move_imag_1 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship_move_1.png')), 0.2)
ship_move_imag_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship_move_2.png')), 0.2)

ship_imag = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship.png')), 0.2)
ship_imag_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship2.png')), 0.1)
bullet_imag = func.scale_image(pygame.image.load(os.path.join(img_folder,'bullet.png')), 0.2)
#############################################################################################

def main():
    Ship([ship_imag_2], shoot_sound, 100, 100)
    Ship([ship_imag_2], shoot_sound, 200, 300)
    player_ship = Player_Ship([ship_imag, ship_move_imag_1, ship_move_imag_2], shoot_sound, 400, 200)
    # camera = Camera()


    # Главный цикл
    running = True
    while running:   
        camera_speed = 10
        camera_x = 0
        camera_y = 0 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player_ship.shoot()
        
                
        #--------------------------------
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            camera_x += camera_speed
        if key[pygame.K_RIGHT]:
            camera_x -= camera_speed
        if key[pygame.K_UP]:
            camera_y += camera_speed
        if key[pygame.K_DOWN]:
            camera_y -= camera_speed
    
        #--------------------------------
        if background_rect[0] > background_rect[2]:
            background_rect[0] = 0
        if background_rect[0] < -background_rect[2]:
            background_rect[0] = 0
        if background_rect[1] > background_rect[3]:
            background_rect[1] = 0    
        if background_rect[1] < -background_rect[3]:
            background_rect[1] = 0 
        #--------------------------------
        background_rect[0] += camera_x /10
        background_rect[1] += camera_y /10
        #--------------------------------
        background_rect_u = background_rect.copy()
        background_rect_d = background_rect.copy()
        background_rect_l = background_rect.copy()
        background_rect_r = background_rect.copy()
        #--------------------------------
        background_rect_u[1] -= background_rect[3]
        background_rect_l[0] -= background_rect[2]
        background_rect_d[1] += background_rect[3]
        background_rect_r[0] += background_rect[2]
        #--------------------------------
        background_rect_u_l = background_rect_u.copy()
        background_rect_u_r = background_rect_u.copy()
        background_rect_d_r = background_rect_d.copy()
        background_rect_d_l = background_rect_d.copy()
        #--------------------------------
        background_rect_u_l[0] -= background_rect[2]
        background_rect_u_r[0] += background_rect[2]
        background_rect_d_l[0] -= background_rect[2]
        background_rect_d_r[0] += background_rect[2] 
        
        
        screen.fill(WHITE)
        screen.blit(background, background_rect)
        screen.blit(background, background_rect_u)
        screen.blit(background, background_rect_l)
        screen.blit(background, background_rect_r)
        screen.blit(background, background_rect_d)
        
        screen.blit(background, background_rect_u_l)
        screen.blit(background, background_rect_u_r)
        screen.blit(background, background_rect_d_l)
        screen.blit(background, background_rect_d_r)
        
        
        
        for i in Sprite().list_draw:
            i.x += camera_x
            i.y += camera_y
            i.update()
            i.draw(screen)

        # camera.draw()

        text = f"x {round(player_ship.x)} y {round(player_ship.y)}"
        draw_text(screen, text, 30, 100, 10)    

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()



try:
    main()
except Exception as e:
    print (e.message, e.args)
    input()
