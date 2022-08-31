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
# import time

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
    list_sun = []
    list_planets = []
    list_iface = []

class Ship(Sprite):
    def __init__(self, ship_type, image_list, shoot_sound, x, y): 
        Sprite().list_draw.append(self)
        Sprite().list_ships.append(self)
        self.ship_type = ship_type
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
        self.angle_to_planet = 0
        self.planet_target = 0
        self.planet_target_status = 0


    def move_to_target(self):
        target = Sprite.list_planets[self.planet_target]
        y = target.planet_y - self.y
        x = target.planet_x - self.x
        self.angle_to_planet = math.degrees(math.atan2(x, y)) - 180
        self.angle_target = self.angle_to_planet
        
        # смена траргета по прибытии на планету
        if x < 1 and y < 1:
            self.planet_target_status = 1
        
        if self.planet_target_status:
            self.planet_target = randint(0, 2)
            self.planet_target_status = 0

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
        
        # плавный поворот на угол таргета (без разворотов на 360)
        if abs(self.angle_front - self.angle_target) > 5 and abs(self.angle_front - self.angle_target) < 359:
            if self.angle_front > self.angle_target:
                self.angle_front += self.rotation_vel
            else:
                self.angle_front -= self.rotation_vel
        else:
            self.angle_front = self.angle_target
      
            
        self.rot()
        self.move()
        self.move_to_target()
        
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

    def text(self):
        text = f"БОТ x {round(self.x)} y {round(self.y)}"
        draw_text(screen, text, 30, 200, 10)   
        
class Player_Ship(Ship):
    def text(self):
        text = f"ИГРОК x {round(self.x)} y {round(self.y)}"
        draw_text(screen, text, 30, 200, 40)   
    
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
        self.text()
    
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
        self.hp = 150

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

class Solar(Sprite):
    def __init__(self, star_imag):
        Sprite().list_sun.append(self)
        Sprite().list_draw.append(self)
        self.image = star_imag
        self.rect = self.image.get_rect()
        self.x = WIDTH/2 - self.rect[2]/2
        self.y = HEIGHT/2 - self.rect[3]/2
        self.centerx = self.x + self.rect[2]/2
        self.centery = self.y + self.rect[3]/2
        
    def update(self):
        pass
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def create_planet(self, radius, speed):
        Planet(planet_imag, radius, speed, self.centerx, self.centery)

class Planet(Sprite):
    def __init__(self, planet_imag, radius, speed, sol_x, sol_y):
        Sprite().list_draw.append(self)
        Sprite().list_planets.append(self)
        self.image = planet_imag
        self.rect = self.image.get_rect()
        self.planet_x = 0
        self.planet_y = 0
        self.x = sol_x
        self.y = sol_y
        self.orbit_angle = 0
        self.orbit_radius = radius
        self.orbit_speed = speed
        
    def move(self):
        if self.orbit_angle > 360:
            self.orbit_angle = 0
        orbit_angle_rad = math.radians(self.orbit_angle) 
        self.planet_x = self.orbit_radius * math.cos(orbit_angle_rad) + self.x - self.rect[2]/2
        self.planet_y = self.orbit_radius * math.sin(orbit_angle_rad) + self.y - self.rect[3]/2
        self.orbit_angle += self.orbit_speed
    
    
    def update(self):
        self.move()
    
    def draw(self, screen):
        screen.blit(self.image, (self.planet_x, self.planet_y))

    def text(self):
        text = f"ПЛАНЕТА x {round(self.planet_x)} y {round(self.planet_y)}"
        draw_text(screen, text, 30, 200, 100)   

class MiniMap(Sprite):
    def __init__(self, x, y):
        Sprite.list_iface.append(self)
        self.x = x
        self.y = y
        self.size_map = 300
        self.size_ship = 5
        self.size_sun = 35
        self.size_planet = 15
        self.scale = 10
        
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size_map, self.size_map))
        # центрирование координат по солнцу
        d_x = self.size_map/2 - Sprite.list_sun[0].x / self.scale - self.size_sun/2
        d_y = self.size_map/2 - Sprite.list_sun[0].y / self.scale - self.size_sun/2
        # отрисовка солнца
        sun_x = Sprite.list_sun[0].x / self.scale + self.x + d_x
        sun_y = Sprite.list_sun[0].y / self.scale + self.y + d_y
        pygame.draw.rect(screen, YELLOW, (sun_x, sun_y, self.size_sun, self.size_sun))
        # отрисовка планет
        for p in Sprite.list_planets:
            planet_x = p.planet_x / self.scale + self.x + d_x
            planet_y = p.planet_y / self.scale + self.y + d_y
            color = BROWN
            pygame.draw.rect(screen, color, (planet_x, planet_y, self.size_planet, self.size_planet))
        # отрисовка остальных кораблей
        for i in Sprite.list_ships:
            ship_x = i.x / self.scale + self.x + d_x
            ship_y = i.y / self.scale + self.y + d_y
            if i.ship_type == 'Player':
                color = GREEN
            else:
                color = BLACK
            if  (ship_x > self.x and ship_x < self.x + self.size_map and
                ship_y > self.y and ship_y < self.y + self.size_map):
                pygame.draw.rect(screen, color, (ship_x, ship_y, self.size_ship, self.size_ship))

        

class Camera():
    def __init__(self, background):
        self.camera_speed = 1
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.background = background
        self.background_rect = self.background.get_rect()

    def update(self):
        self.camera_x = 0.0
        self.camera_y = 0.0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.camera_x += self.camera_speed
        if key[pygame.K_RIGHT]:
            self.camera_x -= self.camera_speed
        if key[pygame.K_UP]:
            self.camera_y += self.camera_speed
        if key[pygame.K_DOWN]:
            self.camera_y -= self.camera_speed
        # свиг
        self.background_rect[0] += self.camera_x
        self.background_rect[1] += self.camera_y
        # зацикленность фона
        if self.background_rect[0] > self.background_rect[2]:
            self.background_rect[0] = 0
        if self.background_rect[0] < -self.background_rect[2]:
            self.background_rect[0] = 0
        if self.background_rect[1] > self.background_rect[3]:
            self.background_rect[1] = 0    
        if self.background_rect[1] < -self.background_rect[3]:
            self.background_rect[1] = 0 
        # копии фона с 8 сторон
        self.background_rect_u = self.background_rect.copy()
        self.background_rect_d = self.background_rect.copy()
        self.background_rect_l = self.background_rect.copy()
        self.background_rect_r = self.background_rect.copy()
        #--------------------------------
        self.background_rect_u[1] -= self.background_rect[3]
        self.background_rect_l[0] -= self.background_rect[2]
        self.background_rect_d[1] += self.background_rect[3]
        self.background_rect_r[0] += self.background_rect[2]
        #--------------------------------
        self.background_rect_u_l = self.background_rect_u.copy()
        self.background_rect_u_r = self.background_rect_u.copy()
        self.background_rect_d_r = self.background_rect_d.copy()
        self.background_rect_d_l = self.background_rect_d.copy()
        #--------------------------------
        self.background_rect_u_l[0] -= self.background_rect[2]
        self.background_rect_u_r[0] += self.background_rect[2]
        self.background_rect_d_l[0] -= self.background_rect[2]
        self.background_rect_d_r[0] += self.background_rect[2] 

    def draw(self, screen):
        # отрисовка фона
        screen.fill(WHITE)
        screen.blit(self.background, self.background_rect)
        screen.blit(self.background, self.background_rect_u)
        screen.blit(self.background, self.background_rect_l)
        screen.blit(self.background, self.background_rect_r)
        screen.blit(self.background, self.background_rect_d)
        screen.blit(self.background, self.background_rect_u_l)
        screen.blit(self.background, self.background_rect_u_r)
        screen.blit(self.background, self.background_rect_d_l)
        screen.blit(self.background, self.background_rect_d_r)




############################################################################################
WIDTH = 1920  # ширина игрового окна
HEIGHT = 1080 # высота игрового окна
FPS = 60 # частота кадров в секунду
BROWN = (100,50,50)
GREEN = (50,255,0)
YELLOW = (255,210,0)
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
ship_move_imag_1 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship_move_1.png')), 0.1)
ship_move_imag_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship_move_2.png')), 0.1)

ship_imag = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship.png')), 0.1)
ship_imag_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ship2.png')), 0.05)
ship_imag_2 = ship_imag_2.convert_alpha()
#--------------------------------
bullet_imag = func.scale_image(pygame.image.load(os.path.join(img_folder,'bullet.png')), 0.2)
#--------------------------------
solar_imag = func.scale_image(pygame.image.load(os.path.join(img_folder,'solar.png')), 0.2)
planet_imag = func.scale_image(pygame.image.load(os.path.join(img_folder,'planet.png')), 0.2)
#############################################################################################

def main():
    Ship('bot', [ship_imag_2], shoot_sound, 100, 100)
    Ship('bot', [ship_imag_2], shoot_sound, 700, 600)
    Ship('bot', [ship_imag_2], shoot_sound, 120, 100)
    Ship('bot', [ship_imag_2], shoot_sound, 600, 900)
    Ship('bot', [ship_imag_2], shoot_sound, 103, 600)


    player_ship = Player_Ship('Player', [ship_imag, ship_move_imag_1, ship_move_imag_2], shoot_sound, 400, 200)
    solar = Solar(solar_imag)
    solar.create_planet(300, 0.5)
    solar.create_planet(500, 0.3)
    solar.create_planet(800, 0.1)
    

    m_map = MiniMap(WIDTH - 300, 0)

    cam = Camera(background)

    # Главный цикл
    running = True
    while running:   
        # camera_speed = 1
        # camera_x = 0.0
        # camera_y = 0.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player_ship.shoot()
        #--------------------------------
        # key = pygame.key.get_pressed()
        # if key[pygame.K_LEFT]:
        #     camera_x += camera_speed
        # if key[pygame.K_RIGHT]:
        #     camera_x -= camera_speed
        # if key[pygame.K_UP]:
        #     camera_y += camera_speed
        # if key[pygame.K_DOWN]:
        #     camera_y -= camera_speed
        # # зацикленность фона
        # if background_rect[0] > background_rect[2]:
        #     background_rect[0] = 0
        # if background_rect[0] < -background_rect[2]:
        #     background_rect[0] = 0
        # if background_rect[1] > background_rect[3]:
        #     background_rect[1] = 0    
        # if background_rect[1] < -background_rect[3]:
        #     background_rect[1] = 0 
        
        
        # фокус камеры на игроке
        # if key[pygame.K_f]:
        # player_focus_x = (player_ship.rect_rot.centerx - WIDTH/2) /100
        # player_focus_y = (player_ship.rect_rot.centery - HEIGHT/2) /100
        # camera_x = -player_focus_x 
        # camera_y = -player_focus_y 

        # if player_ship.rect_rot.centerx < WIDTH/2:
        #     camera_x += camera_speed
        

       
        # # свдиг фона
        # background_rect[0] += camera_x
        # background_rect[1] += camera_y

        # # копии фона с 8 сторон
        # background_rect_u = background_rect.copy()
        # background_rect_d = background_rect.copy()
        # background_rect_l = background_rect.copy()
        # background_rect_r = background_rect.copy()
   
        # #--------------------------------
        # background_rect_u[1] -= background_rect[3]
        # background_rect_l[0] -= background_rect[2]
        # background_rect_d[1] += background_rect[3]
        # background_rect_r[0] += background_rect[2]
       
        # #--------------------------------
        # background_rect_u_l = background_rect_u.copy()
        # background_rect_u_r = background_rect_u.copy()
        # background_rect_d_r = background_rect_d.copy()
        # background_rect_d_l = background_rect_d.copy()
       
        # #--------------------------------
        # background_rect_u_l[0] -= background_rect[2]
        # background_rect_u_r[0] += background_rect[2]
        # background_rect_d_l[0] -= background_rect[2]
        # background_rect_d_r[0] += background_rect[2] 
        
        # # отрисовка фона
        # screen.fill(WHITE)
        # screen.blit(background, background_rect)
        # screen.blit(background, background_rect_u)
        # screen.blit(background, background_rect_l)
        # screen.blit(background, background_rect_r)
        # screen.blit(background, background_rect_d)
        # screen.blit(background, background_rect_u_l)
        # screen.blit(background, background_rect_u_r)
        # screen.blit(background, background_rect_d_l)
        # screen.blit(background, background_rect_d_r)
        
        cam.update()
        cam.draw(screen)
        
        
        # остальные объекты
        for i in Sprite().list_draw:
            i.update()
            i.x += cam.camera_x * 10
            i.y += cam.camera_y * 10
            i.draw(screen)

        # интерфейс
        m_map.draw(screen)


        
        # text = f"player_focus_x {player_focus_x} player_focus_y {player_focus_y}"
        # draw_text(screen, text, 30, 600, 10)   
        # text = f"camera_x {camera_y} camera_y {camera_y}"
        # draw_text(screen, text, 30, 600, 40)  
        # text = f"background_rect[0] {background_rect[0]} background_rect[1] {background_rect[1]}"
        # draw_text(screen, text, 30, 600, 70)  
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

try:
    main()
except Exception as e:
    print (e.message, e.args)
    input()
