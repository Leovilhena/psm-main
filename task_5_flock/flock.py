# Task
# Suggest and implement your own version of the Flock computer application
# so that you can have a greater impact on the behavior of animated objects and the quality of scenes.
import pygame as pg
from pygame.math import Vector2 as vec
import traceback
from random import randint, uniform
from math import sin, cos
from abc import ABC

black = (0, 0, 0)
white = (255, 255, 255)
grey = (100, 100, 100)
light_grey = (200, 200, 200)
red = (255, 0, 0)

# constants for the window and user interface size
width = 800
height = 600
gui_height = 100


# ------------- helper functions ----------------------------------------------

def limit(vector: vec, length: float) -> None:
    """
    Limit a vector to a given length
    :param vector: vector input
    :type vector: vec
    :param length: length constraint
    :type length: float
    :return: None
    """
    if vector.length_squared() <= length**2:
        return
    else:
        vector.scale_to_length(length)


def remap(n: float, start1: float, stop1: float, start2: float, stop2: float) -> float:
    """
    Re-maps a number from one range to another

    :param n: the incoming value to be converted
    :type n: float
    :param start1: lower bound of the value's current range
    :type start1: float
    :param stop1: upper bound of the value's current range
    :type stop1: float
    :param start2: lower bound of the value's target range
    :type start2: float
    :param stop2: upper bound of the value's target range
    :type stop2: float
    :return: float
    """
    new_value = (n - start1) / (stop1 - start1) * (stop2 - start2) + start2
    if start2 < stop2:
        return constrain(new_value, start2, stop2)
    else:
        return constrain(new_value, stop2, start2)


def constrain(n: float, low: float, high: float) -> float:
    """
    Enforces a value to inside the maximum boundary
    :param n: new value for constraining
    :type n: float
    :param low: lower bound
    :type low: float
    :param high: upper bound
    :type high: float
    :return: float
    """
    return max(min(n, high), low)


def get_boid_color(index: int, count: int) -> tuple:
    """
    Generates different RGB values for coloring the boids
    :param index: current boid index
    :type index: int
    :param count: number of boids
    :type count: int
    :return: tuple
    """
    color_red = round(index * 255 / count)
    color_green = round((count - index) * 255 / count)
    color_blue = 255
    return color_red, color_green, color_blue
# -----------------------------------------------------------------------------


class Game:
    """Main Game object for rendering and controlling the game"""
    def __init__(self, boids_count: int = 100):
        pg.init()
        pg.display.set_caption("Flock simulation")
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((width, height))
        self.screen_rect = self.screen.get_rect()
        self.screen_rect.h -= gui_height
        self.fps = 60
        self.all_sprites = pg.sprite.Group()
        self.gui_elements = pg.sprite.Group()
        self.font = pg.font.SysFont('Arial', 18)
        self.player = Player(self, (400, 300))
        self.running = None

        # generate boids
        for i in range(boids_count):
            pos = (randint(0, 800), randint(0, 600))
            color = get_boid_color(i, boids_count)
            Boid(self, pos, color)

        # create sliders for adjusting the flocking behavior
        self.slider1 = Slider(self, (20, height - gui_height), 'alignment')
        self.slider2 = Slider(self, (260, height - gui_height), 'separation')
        self.slider3 = Slider(self, (500, height - gui_height), 'cohesion')

    def events(self) -> None:
        """
        Check for Pygame events
        :return: None
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def update(self) -> None:
        """
        Update Pygame sprites and elements
        :return: None
        """
        self.all_sprites.update()
        self.gui_elements.update()

    def draw(self) -> None:
        """
        Draw the game screen, sprites and elements
        :return: None
        """
        self.screen.fill(black)
        self.all_sprites.draw(self.screen)

        # draw the interface with the sliders
        self.screen.fill(black, ((0, self.screen_rect.h), (width, gui_height)))
        self.gui_elements.draw(self.screen)

        pg.display.update()

    def run(self) -> None:
        """
        Runs game by checking running bool, events, updating and drawing to the screen
        :return: None
        """
        self.running = True
        while self.running:
            self.clock.tick(self.fps)
            self.events()
            self.update()
            self.draw()

        pg.quit()


class PhysicsObject(ABC, pg.sprite.Sprite):
    """Abstract class for all sprites that experience physics"""
    def __init__(self, game: Game, position: tuple):
        super().__init__(game.all_sprites)
        self.game = game
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.pos = vec(position)
        # the velocity vector gets multiplied by the speed and friction values
        self.speed = 1
        # smaller friction value = more friction (makes sense!?)
        self.friction = 0.9

    def update(self) -> None:
        """
        Updates the physics parameters for inherited object
        :return: None
        """
        self.vel += self.acc
        self.pos += self.vel * self.speed
        # reset acceleration
        self.acc *= 0
        # apply friction
        self.vel *= self.friction

        # wrap around the edges of the screen
        if self.pos.x > self.game.screen_rect.w:
            self.pos.x = -self.rect.w
        elif self.pos.x < -self.rect.h:
            self.pos.x = self.game.screen_rect.w
        if self.pos.y > self.game.screen_rect.h:
            self.pos.y = -self.rect.h
        elif self.pos.y < -self.rect.h:
            self.pos.y = self.game.screen_rect.h

        self.rect.topleft = self.pos


class Player(PhysicsObject):
    """Player's object for moving around the red dot"""
    def __init__(self, game: Game, position: tuple):
        super().__init__(game, position)
        x = y = 30
        self.image = pg.Surface((x, y))
        pg.draw.circle(self.image, red, (x / 2, y / 2), 5)
        self.rect = self.image.get_rect()
        self.speed = 0.5

    def update(self) -> None:
        """
        Updates Player position
        :return: None
        """
        # steer player with WASD keys
        keys = pg.key.get_pressed()
        self.acc.x = keys[pg.K_d] - keys[pg.K_a]
        self.acc.y = keys[pg.K_s] - keys[pg.K_w]
        # normalize the acceleration vector
        limit(self.acc, 1.0)
        super().update()


class Boid(PhysicsObject):
    """Boid/flock object"""
    def __init__(self, game: Game, position: tuple, color: tuple):
        super().__init__(game, position)
        x = y = 20
        self.image = pg.Surface((x, y))
        self.image.set_colorkey(black)
        pg.draw.circle(self.image, color, (x / 2, y / 2), 4)
        self.rect = self.image.get_rect()

        self.speed = randint(2, 3)
        self.max_force = 0.3
        self.friction = 0.75
        self.target = vec(0, 0)
        self.extent = vec(0, 0)
        self.theta = 0

    def update(self) -> None:
        """
        Updates boid position
        :return: None
        """
        # seek a target
        self.acc += self.wander()

        # flocking behavior
        alignment = self.alignment()
        separation = self.separation()
        cohesion = self.cohesion()
        # adjust the vectors according to the chosen slider values
        alignment *= self.game.slider1.get_slider_value()
        separation *= self.game.slider2.get_slider_value()
        cohesion *= self.game.slider3.get_slider_value()
        # add flocking to the acceleration vector
        self.acc += alignment
        self.acc += separation
        self.acc += cohesion
        super().update()

    def alignment(self) -> vec:
        """
        Causes a boid to line up with others close by.
        :return vec
        """
        perception_radius = 40
        steering = vec(0, 0)
        total = 0
        for other in self.game.all_sprites:
            if other != self:
                dist = other.pos.distance_to(self.pos)
                if dist < perception_radius:
                    steering += other.vel
                    total += 1
        if total > 0:
            steering *= 1 / total
            steering -= self.vel
            limit(steering, self.max_force)

        return steering

    def separation(self) -> vec:
        """
        Causes boid to steer away from all of its neighbors
        :return: vec
        """
        perception_radius = 40
        steering = vec(0, 0)
        total = 0
        for other in self.game.all_sprites:
            if other != self:
                d = self.pos - other.pos
                dist = d.length()
                if dist < perception_radius:
                    d /= (dist * dist)
                    steering += d
                    total += 1
        if total > 0:
            steering /= total
            steering.scale_to_length(self.speed)
            steering -= self.vel
            limit(steering, self.max_force)

        return steering

    def cohesion(self) -> vec:
        """
        Causes boid to steer towards the "center of mass",the average position of other boids within a perception radius
        :return: vec
        """
        perception_radius = 80
        steering = vec(0, 0)
        total = 0
        for other in self.game.all_sprites:
            if other != self:
                dist = other.pos.distance_to(self.pos)
                if dist < perception_radius:
                    steering += other.pos
                    total += 1
        if total > 0:
            steering *= 1 / total
            steering -= self.pos
            steering.scale_to_length(self.speed)
            steering -= self.vel
            limit(steering, self.max_force)

        return steering

    def arrive(self, target) -> vec:
        """
        Make the boid move to a target position
        :param target: position we are targeting
        :type target: vec
        :return: vec
        """
        desired = target - self.pos
        d = desired.length()
        desired = desired.normalize()
        radius = 100.0

        if d < radius:
            m = remap(d, 0.0, radius, 0.0, self.speed)
            desired *= m
        else:
            desired *= self.speed

        # calculate steering force
        steering = desired - self.vel
        limit(steering, self.max_force)

        return steering

    def wander(self) -> vec:
        """
        Calculates a target that changes slightly each frame by a random angle
        :return: vec
        """
        if self.vel.length_squared() != 0:
            # extent vector as a multiple of the velocity
            self.extent = self.vel.normalize() * 80
            # radius
            r = 30
            # change the angle by a small random amount each frame
            self.theta += uniform(-1, 1) / 16
            self.target = self.pos + self.extent + vec(r * cos(self.theta),
                                                       r * sin(self.theta))

        return self.arrive(self.target)


class Slider(pg.sprite.Sprite):
    """Slider for controlling flocking parameters"""
    def __init__(self, game: Game, pos: tuple, text: str):
        super().__init__(game.gui_elements)
        self.game = game
        self.pos = vec(pos)
        self.text = text
        self.image = pg.Surface((200, 80))
        self.image.fill(black)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.slider_rect = pg.Rect((0, 40), (20, 20))

        font = self.game.font
        self.text = font.render(text, False, white)

    def update(self) -> None:
        """
        Updates slider rendering
        :return: None
        """
        # calculate if mouse is on slider
        m_pos = vec(pg.mouse.get_pos())
        s_pos = self.pos + vec(self.slider_rect.center)
        if s_pos.distance_to(m_pos) < 20:
            if pg.mouse.get_pressed()[0]:
                # change the sliders x value based on mouse x
                self.slider_rect.centerx = m_pos.x - self.pos.x
        self.slider_rect.centerx = constrain(self.slider_rect.centerx, 10, 190)

        # construct the slider's image
        self.image.fill(black)
        pg.draw.line(self.image, light_grey, (0, self.slider_rect.centery),
                     (200, self.slider_rect.centery), 2)
        self.draw_button()

        self.image.blit(self.text, (0, 6))

    def draw_button(self) -> None:
        """
        Draws a pretty button
        :return: None
        """
        surface = self.image
        rect = self.slider_rect
        rect_off = rect.copy()
        rect_off.y -= 3
        pg.draw.ellipse(surface, grey, rect)
        pg.draw.ellipse(surface, white, rect_off)

    def get_slider_value(self) -> float:
        """
        Returns a value from 0 to 1 for sliders
        :return: float
        """
        return (self.slider_rect.centerx - 10) / 180


if __name__ == '__main__':
    try:
        game_obj = Game()
        game_obj.run()
    except:
        traceback.print_exc()
        pg.quit()
