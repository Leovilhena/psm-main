import pygame as pg
import numpy as np


class Grid:
    def __init__(self, width, height, scale, offset, screen):
        self.scale = scale
        self.screen = screen
        self.columns = int(height/scale)
        self.rows = int(width/scale)
        self.size = (self.rows, self.columns)
        # create array of random ints from [0,1]
        self.grid_array = np.random.randint(2, size=self.size)
        self.offset = offset

    def draw(self, color, x, y) -> None:
        """"
        Draws color on grid by coordinates

        :param color tuple RGB values
        :param x int row index
        :param y int column index
        :return None
        """
        y_pos = y * self.scale
        x_pos = x * self.scale
        pg.draw.rect(self.screen, color, [x_pos, y_pos, self.scale-self.offset, self.scale-self.offset])

    def run(self, off_color, on_color) -> None:
        """"
        Runs Conway's Game of Life by checking each point and drawing on the grid changes

        :param off_color tuple RGB values for dead cell
        :param on_color tuple RGB values for live cell
        :return None
        """
        # create new array with same size and only zeros
        next_life = np.zeros(self.size)
        # noinspection PyTypeChecker
        for x, y in np.ndindex(self.size):  # iterate on array
            current_point = self.grid_array[x][y]

            if current_point:
                self.draw(on_color, x, y)
            else:
                self.draw(off_color, x, y)
            # sum number of neighbours around current point
            neighbours = self.get_neighbours_sum(x, y, current_point)

            # if current_point is 0 and has 3 neighbours (reproduction)
            if not current_point and neighbours == 3:
                next_life[x][y] = 1
            # if current_point is 1 and neighbours are less than 2 (underpopulation) or greater than 3 (overpopulation)
            elif current_point and (neighbours < 2 or neighbours > 3):
                next_life[x][y] = 0
            else:
                next_life[x][y] = current_point

        self.grid_array = next_life

    def get_neighbours_sum(self, x, y, current_point) -> int:
        """"
        1. Slice the array to a [3,3] around the x,y point
        2. sum all elements
        3. return the sum all elements minus the current point from the sum which is the one that we are checking

        :param x int row index
        :param y int column index
        :param current_point int [0,1]
        :return int the sum of all surrounding elements - the middle point
        """
        return np.sum(self.grid_array[x-1:x+2, y-1:y+2]) - current_point
