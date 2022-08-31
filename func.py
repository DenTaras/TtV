import pygame


def scale_image(img, scal):
    size = round(img.get_width() * scal), round(img.get_height() * scal)
    return pygame.transform.scale(img, size)

def draw_text(surf, text_list):
    size = 30
    font_name = pygame.font.match_font('arial')
    color = pygame.Color('white')
    font = pygame.font.Font(font_name, size)
    x = 10
    y = 10
    for text in text_list:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midleft = (x, y)
        surf.blit(text_surface, text_rect)
        y += 30