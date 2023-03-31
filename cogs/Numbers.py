from lib2to3.pytree import convert
import cv2
import pygame as pg
import os
from math import ceil, floor
from PIL import Image
TEXT_WIDTH = 6 # on font size 12 monocraft medium
TEXT_HEIGHT = 11
RESOLUTION_FACTOR = 2
WHITE = (255,255,255)
Numbers = []

# Server has no video devices!
os.environ["SDL_VIDEODRIVER"] = "dummy"

def ImageToNumbers(ImagePath, Shades):

    for i in range(0, Shades):
        Numbers.append(str(i))

    if ImagePath[-3:] != "png":
        Image1 = Image.open(ImagePath)
        ImagePath = ImagePath[:-3]+"png"
        Image1.save(ImagePath)

    pg.init()
    font = pg.font.SysFont("Monocraft Medium", 12)
    Img = cv2.imread(ImagePath, 0)

    HEIGHT, WIDTH = Img.shape
    WIDTH *= RESOLUTION_FACTOR
    HEIGHT *= RESOLUTION_FACTOR

    GRID_WIDTH = WIDTH // TEXT_WIDTH
    GRID_HEIGHT = HEIGHT // TEXT_HEIGHT

    w = pg.display.set_mode((GRID_WIDTH * TEXT_WIDTH, GRID_HEIGHT * TEXT_HEIGHT))
    Img = cv2.resize(Img, (GRID_WIDTH, GRID_HEIGHT), interpolation=cv2.INTER_AREA)

    for pixel_x in range(GRID_WIDTH):

        for pixel_y in range(GRID_HEIGHT):

            brightness = Img[pixel_y][pixel_x]
            num = ceil(brightness / (255/Shades))  # Map to 0-1, 255/num

            if num == 0:
                continue

            r_num = None # rendered num
            r_num = font.render(Numbers[num-1],1,WHITE)
            w.blit(r_num,(pixel_x*TEXT_WIDTH,pixel_y*TEXT_HEIGHT))

    pg.display.update()
    pg.image.save(w, ImagePath[:-4]+"_num.png")
    pg.quit()
