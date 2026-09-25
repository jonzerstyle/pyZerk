import pygame
import movement
import globals
import highscore

class Class_ProcessKeybo():
    def __init__(self):
        self.collisionOn = 0
        self.running = 1
        self.fullscreen = 0
        self.return_to_menu = False

    def run(self, screensize, screen, screen_backcolor, mainContC, events=None):
        self.return_to_menu = False
        keys = pygame.key.get_pressed()

        # totally wierd SPACE key is blocked
        # if up left done with arrow keys!
        # switch to left control instead
        if keys[pygame.K_LCTRL] == 1:
            mainContC.addItem("player_fire", "shoot")
        else:
            mainContC.addItem("player_fire", "ceasefire")

        #assign player movement based on keys pressed
        #   test for simultaneous keys first
        #       upleft, upright, downleft, downright
        #   next:
        #       test singles
        if keys[pygame.K_UP] == 1 and keys[pygame.K_LEFT] == 1:
            mainContC.addItem("player_movement", movement.dirEnum.UPLEFT)
        elif keys[pygame.K_UP] == 1 and keys[pygame.K_RIGHT] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.UPRIGHT)
        elif keys[pygame.K_DOWN] == 1 and keys[pygame.K_LEFT] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.DOWNLEFT)
        elif keys[pygame.K_DOWN] == 1 and keys[pygame.K_RIGHT] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.DOWNRIGHT)
        #test single keys
        elif keys[pygame.K_UP] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.UP)
        elif keys[pygame.K_DOWN] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.DOWN)
        elif keys[pygame.K_LEFT] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.LEFT)
        elif keys[pygame.K_RIGHT] == 1: 
            mainContC.addItem("player_movement", movement.dirEnum.RIGHT)
        else:
            mainContC.addItem("player_movement", movement.dirEnum.NONE)

        if events is None:
            events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                if not highscore.is_web_env():
                    self.running = 0
                else:
                    self.return_to_menu = True
                    globals.MENUON = True
            elif event.type == pygame.KEYDOWN: 
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.return_to_menu = True
                    globals.MENUON = True
                elif event.key == pygame.K_F11:
                    if self.fullscreen == 0:
                        pygame.display.set_mode(screensize, pygame.FULLSCREEN)
                        pygame.mouse.set_visible(False)
                        screen.fill((screen_backcolor))
                        pygame.display.flip()
                        self.fullscreen = 1
                    else:
                        pygame.display.set_mode(screensize)
                        pygame.mouse.set_visible(True)
                        screen.fill((screen_backcolor))
                        pygame.display.flip()
                        self.fullscreen = 0
