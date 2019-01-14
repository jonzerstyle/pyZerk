import pygame
import copy
import globals

fontSize = 50

class Class_Text(pygame.sprite.Sprite):
    def __init__(self, pos, text, color, size = fontSize, groups = []):
        pygame.sprite.Sprite.__init__(self, groups + [globals.TEXT])
        self.pos = copy.deepcopy(pos)
        self.font = pygame.font.Font(None, fontSize)
        self.size = copy.deepcopy(size)
        self.text = copy.deepcopy(text)
        self.color = copy.deepcopy(color)
    def update(self, text):
        self.text = copy.deepcopy(text)
    def setBold(self, arg):
        self.font.set_bold(arg)
    def getBold(self):
        return self.font.get_bold()
    def draw(self, surface):
        dirtyrects = []
        fontSurface = self.font.render(self.text, True, self.color)
        dirtyrects.append(surface.blit(fontSurface, self.pos))
        return dirtyrects
        
