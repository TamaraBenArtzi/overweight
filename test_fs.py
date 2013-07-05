import pygame
pygame.display.init()
s=pygame.display.set_mode((1366,768), pygame.FULLSCREEN)
import time
time.sleep(1)
pygame.display.iconify()
time.sleep(1)
pygame.display.toggle_fullscreen()
time.sleep(1)
pygame.display.iconify()
time.sleep(3)
