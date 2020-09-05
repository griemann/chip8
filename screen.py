import pygame as pg

BLACK = (0x00, 0x00, 0x00)
WHITE = (0xFF, 0xFF, 0xFF)
COLOURS = [BLACK, WHITE] #COLOURS[0] is the background, COLOURS[1] is the pixel colour.

class Screen:
    def __init__(self, scale: int=1) -> None:
        self.cols = 64
        self.rows = 32
        self.scale = scale
        self.surface = pg.display.set_mode((self.cols * self.scale, self.rows * self.scale))

        self.clear_screen()

    def prepare_frame(self, framebuffer) -> None:
        # prepare to draw the next frame given by the framebuffer
        pass

    def draw_pixel(self, x: int, y: int, colour: int) -> None:
        coords = pg.Rect(x * self.scale, y * self.scale, self.scale, self.scale)
        self.surface.fill(self.surface, COLOURS[colour], coords)

    def clear_screen(self):
        self.surface.fill(COLOURS[0])

    @staticmethod
    def draw() -> None:
        """
        Draw a new frame.
        """
        pg.display.flip()

    @staticmethod
    def quit():
        pg.display.quit()
    