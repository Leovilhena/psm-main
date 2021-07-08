# Task
# Build a computer application that implements your own version of the Game of Life.
import pygame as pg
from helpers import Grid

# global variables
width, height = 800, 800
size = (width, height)
fps = 20
blue = (0, 14, 71)
white = (255, 255, 255)
scale = 8
offset = 1


def main():
    pg.init()
    pg.display.set_caption("Conway's Game of Life")
    screen = pg.display.set_mode(size)
    clock = pg.time.Clock()

    grid = Grid(width, height, scale, offset, screen)

    while True:
        clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

        grid.run(off_color=blue, on_color=white)
        pg.display.update()


if __name__ == '__main__':
    main()
