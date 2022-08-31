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
import func


class Sprite():
    list_draw = []
    list_ships = []
    list_bullets = []
    list_sun = []
    list_planets = []
    list_iface = []

    player_star_sistem = 1
    star_sistem = {1: [],
                   2: []}


class Ship(Sprite):
    def __init__(self, star_sistem, ship_type, image_list, shoot_sound, x, y):
        Sprite().list_draw.append(self)
        Sprite().list_ships.append(self)
        Sprite().star_sistem[star_sistem].append(self)
        self.star_sistem = star_sistem
        self.ship_type = ship_type
        # спрайт и его анимация
        self.x = x
        self.y = y
        self.image_list = image_list
        self.image = self.image_list[0]
        self.image_rot = self.image
        self.rect = self.image.get_rect()
        self.timer = 0
        self.anim_count = 0
        self.time_count = 0
        # параметры корабля
        self.name = 'ship_name'
        self.angle_front = 0
        self.angle_target = 0
        self.rotation_vel = 3
        self.speed = 0
        self.speed_up = 0.1
        # ИИ
        self.angle_to_planet = 0
        self.planet_target = 0
        self.planet_target_status = 0

    def move_to_target(self):
        # направление в сторону цели
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
        self.rect = self.image_rot.get_rect(center=(self.x, self.y))

    def anim_image(self):
        if self.anim_count > len(self.image_list) - 2:
            self.anim_count = 0
        else:
            self.anim_count += 1
        self.image = self.image_list[self.anim_count]

    def update(self):
        if self.speed < 4:
            self.speed += self.speed_up

        # плавный поворот на угол таргета (без разворотов на 360)
        if 5 < abs(self.angle_front - self.angle_target) < 359:
            if self.angle_front > self.angle_target:
                self.angle_front += self.rotation_vel
            else:
                self.angle_front -= self.rotation_vel
        else:
            self.angle_front = self.angle_target

        self.check_colise_bullet()
        self.rot()
        self.move()
        self.move_to_target()

    def draw(self, screen):
        if self.time_count == 10:
            self.anim_image()
            self.time_count = 0
        else:
            self.time_count += 1
        screen.blit(self.image_rot, self.rect)
        # тестовые точки
        pygame.draw.circle(screen, pygame.Color('red'), (self.x, self.y), 5)
        target = Sprite.list_planets[self.planet_target]
        pygame.draw.line(screen, pygame.Color('blue'), (self.x, self.y), (target.planet_x, target.planet_y))

        # self.draw_HUD(screen)

    def draw_HUD(self, screen):
        size = 30
        font_name = pygame.font.match_font('arial')
        color = pygame.Color('white')
        font = pygame.font.Font(font_name, size)
        x = self.x
        y = self.y - 60
        text_surface = font.render(self.name, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        screen.blit(text_surface, text_rect)

    def shoot(self):
        Bullet(self.star_sistem, self, bullet_imag, self.x, self.y,
               self.angle_front, self.speed)
        shoot_sound.play()

    def kill(self):
        Explosion(1, boom_imag, self.x, self.y)
        boom_sound.play()
        Sprite().list_draw.remove(self)
        Sprite().list_ships.remove(self)
        Sprite().star_sistem[self.star_sistem].remove(self)

    def check_colise_bullet(self):
        for bul in Sprite().list_bullets:
            if bul.source == self:
                continue
            else:
                if abs(self.x - bul.x) < 20 and abs(self.y - bul.y) < 20:
                    bul.kill()
                    self.kill()


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


class Bullet(Sprite):
    def __init__(self, star_sistem, source, bullet_imag, x, y, angle_front, speed):
        Sprite().list_bullets.append(self)
        Sprite().list_draw.append(self)
        Sprite().star_sistem[star_sistem].append(self)
        self.source = source
        self.image = bullet_imag
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.angle_front = angle_front
        self.speed = 20 + speed
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
    def __init__(self, star_sistem, star_imag):
        Sprite().list_sun.append(self)
        Sprite().list_draw.append(self)
        Sprite().star_sistem[star_sistem].append(self)
        self.star_sistem = star_sistem
        self.image = star_imag
        self.rect = self.image.get_rect()
        self.x = WIDTH / 2
        self.y = HEIGHT / 2

    def update(self):
        pass

    def draw(self, screen):
        self.rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, self.rect)
        pygame.draw.circle(screen, pygame.Color('red'), (self.x, self.y), 5)

    def create_planet(self, planet_imag, radius, speed):
        Planet(self.star_sistem, planet_imag, radius, speed, self.x, self.y)


class Planet(Sprite):
    def __init__(self, star_sistem, planet_imag, radius, speed, sol_x, sol_y):
        Sprite().list_draw.append(self)
        Sprite().list_planets.append(self)
        Sprite().star_sistem[star_sistem].append(self)
        self.star_sistem = star_sistem
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
        self.planet_x = self.orbit_radius * math.cos(orbit_angle_rad) + self.x
        self.planet_y = self.orbit_radius * math.sin(orbit_angle_rad) + self.y
        self.orbit_angle += self.orbit_speed

    def create_ship(self):
        Ship(self.star_sistem, 'bot', [ship_imag_2], shoot_sound, self.planet_x, self.planet_y)

    def update(self):
        self.move()

        if len(Sprite().list_ships) < 5:
            self.create_ship()

    def draw(self, screen):
        self.rect = self.image.get_rect(center=(self.planet_x, self.planet_y))
        screen.blit(self.image, self.rect)
        # тестовые точки
        pygame.draw.circle(screen, pygame.Color('red'), (self.planet_x, self.planet_y), 5)


    def text(self):
        text = f"ПЛАНЕТА x {round(self.planet_x)} y {round(self.planet_y)}"
        func.draw_text(screen, text, 30, 200, 100)


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
        d_x = self.size_map / 2 - Sprite.list_sun[0].x / self.scale - self.size_sun / 2
        d_y = self.size_map / 2 - Sprite.list_sun[0].y / self.scale - self.size_sun / 2
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
            if (self.x < ship_x < self.x + self.size_map and
                    self.y < ship_y < self.y + self.size_map):
                pygame.draw.rect(screen, color, (ship_x, ship_y, self.size_ship, self.size_ship))


class Camera():
    def __init__(self, background, player_ship):
        self.camera_speed = 1
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.background = background
        self.background_rect = self.background.get_rect()
        self.background_rect_f = [float(self.background_rect[0]), float(self.background_rect[1])]
        self.focus_target = player_ship
        self.focus_flag = 1

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
        # следование за игроком
        if self.focus_flag:
            self.camera_x -= (self.focus_target.x - WIDTH / 2) / 200
            self.camera_y -= (self.focus_target.y - HEIGHT / 2) / 200

        # свиг
        self.background_rect_f[0] += self.camera_x
        self.background_rect_f[1] += self.camera_y

        self.background_rect[0] = int(self.background_rect_f[0])
        self.background_rect[1] = int(self.background_rect_f[1])
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
        # --------------------------------
        self.background_rect_u[1] -= self.background_rect[3]
        self.background_rect_l[0] -= self.background_rect[2]
        self.background_rect_d[1] += self.background_rect[3]
        self.background_rect_r[0] += self.background_rect[2]
        # --------------------------------
        self.background_rect_u_l = self.background_rect_u.copy()
        self.background_rect_u_r = self.background_rect_u.copy()
        self.background_rect_d_r = self.background_rect_d.copy()
        self.background_rect_d_l = self.background_rect_d.copy()
        # --------------------------------
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

    def focus_on_off(self):
        self.focus_flag = (self.focus_flag + 1) % 2


class Explosion(Sprite):
    def __init__(self, star_sistem, image_full, x, y):
        Sprite().list_draw.append(self)
        Sprite().star_sistem[star_sistem].append(self)
        self.star_sistem = star_sistem
        self.image_full = image_full
        self.image_cur = self.image_full
        self.x = x
        self.y = y
        self.frame_size = self.image_full.get_rect()[2] / 8
        self.frame = [0, 0, self.frame_size, self.frame_size]
        self.frame_step_x = 0
        self.frame_step_y = 0

    def update(self):
        pass

    def kill(self):
        Sprite().list_draw.remove(self)
        Sprite().star_sistem[self.star_sistem].remove(self)

    def next_frame(self):
        if self.frame_step_x < 7:
            self.frame_step_x += 1
        else:
            if self.frame_step_y < 5:
                self.frame_step_x = 0
                self.frame_step_y += 1
            else:
                # self.frame_step_x = 0
                # self.frame_step_y = 0
                self.kill()
        # координаты фремйма рассчитываются из шага и размера фрейма
        self.frame[0] = self.frame_step_x * self.frame_size
        self.frame[1] = self.frame_step_y * self.frame_size

    def draw(self, screen):
        screen.blit(self.image_cur, (self.x - self.frame_size/2, self.y - self.frame_size/2), self.frame)
        self.next_frame()


class Cursor(Sprite):
    def __init__(self):
        self.x, self.y = pygame.mouse.get_pos()

    def draw(self, screen):
        self.x, self.y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, pygame.Color('green'), (self.x, self.y), 5)
        # линия от корабля до курсора
        for i in Sprite.list_ships:
            if i.ship_type == 'Player':
                pygame.draw.line(screen, pygame.Color('green'), (self.x, self.y), (i.x, i.y))


############################################################################################
WIDTH = 1920  # ширина игрового окна
HEIGHT = 1080  # высота игрового окна
FPS = 60  # частота кадров в секунду
BROWN = (100, 50, 50)
GREEN = (50, 255, 0)
YELLOW = (255, 210, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# --------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("through the void")
clock = pygame.time.Clock()

# --------------------------------
# Папки с файлами
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'snd')
# --------------------------------
shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'laser-gun-single-shot.mp3'))
boom_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'boom.mp3'))
# --------------------------------
background = func.scale_image(pygame.image.load(os.path.join(img_folder, 'astro_obj/cosmos.jpg')), 1)
background_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'astro_obj/cosmos_2.jpg')), 1)
# background_rect = background.get_rect()
# --------------------------------
ship_move_imag_1 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ships/ship_move_1.png')), 0.1)
ship_move_imag_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ships/ship_move_2.png')), 0.1)

ship_imag = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ships/ship.png')), 0.1)
ship_imag_2 = func.scale_image(pygame.image.load(os.path.join(img_folder, 'ships/ship2.png')), 0.05)
ship_imag_2 = ship_imag_2.convert_alpha()
# --------------------------------
bullet_imag = func.scale_image(pygame.image.load(os.path.join(img_folder, 'guns/bullet.png')), 0.2)
boom_imag = func.scale_image(pygame.image.load(os.path.join(img_folder, 'boom.png')), 0.6)
# --------------------------------
solar_imag = func.scale_image(pygame.image.load(os.path.join(img_folder, 'astro_obj/solar.png')), 0.2)
planet_imag_er = func.scale_image(pygame.image.load(os.path.join(img_folder, 'astro_obj/planet_er.png')), 0.15)
planet_imag_sat = func.scale_image(pygame.image.load(os.path.join(img_folder, 'astro_obj/planet_sat.png')), 0.4)
planet_imag_jup = func.scale_image(pygame.image.load(os.path.join(img_folder, 'astro_obj/planet_jup.png')), 0.3)


#############################################################################################
def main():
    player_ship = Player_Ship(1, 'Player', [ship_imag, ship_move_imag_1, ship_move_imag_2], shoot_sound, 800, 800)
    solar = Solar(1, solar_imag)
    solar.create_planet(planet_imag_er, 300, 0.2)
    solar.create_planet(planet_imag_sat, 500, 0.15)
    solar.create_planet(planet_imag_jup, 900, 0.1)

    m_map = MiniMap(WIDTH - 300, 0)
    cam = Camera(background, player_ship)
    cursor = Cursor()

    # Главный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player_ship.shoot()
                if event.key == pygame.K_f:
                    cam.focus_on_off()
        # --------------------------------
        cam.update()
        cam.draw(screen)
        # остальные объекты
        for i in Sprite().list_draw:
            i.update()
            i.x += cam.camera_x * 10
            i.y += cam.camera_y * 10
            # отрисовываем только те объекты, которые находятся в текущей звездной системе
            if i in Sprite().star_sistem[Sprite().player_star_sistem]:
                i.draw(screen)
        # интерфейс
        m_map.draw(screen)
        cursor.draw(screen)


        # text = f"player_focus_x {player_focus_x} player_focus_y {player_focus_y}"
        # draw_text(screen, text, 30, 600, 10)   
        # text = f"camera_x {camera_y} camera_y {camera_y}"
        # draw_text(screen, text, 30, 600, 40)
        # --------------------------------
        s1 = Sprite.list_ships[1].planet_target
        s2 = Sprite.list_ships[2].planet_target
        s3 = Sprite.list_ships[3].planet_target
        text = ["F - вкл/выкл следящей камеры",
                "Стрелки - ручная камера",
                "W/S - ускориться/замедлиться",
                "A/D - поворот",
                "Space - стрелять (добирать крипов)",
                f"{s1}",
                f"{s2}",
                f"{s3}"]

        # func.draw_text(screen, text)
        # --------------------------------
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


main()
