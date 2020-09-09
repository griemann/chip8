import pygame as pg

BLACK = (0x00, 0x00, 0x00)
WHITE = (0xFF, 0xFF, 0xFF)
COLOURS = [BLACK, WHITE] #COLOURS[0] is the background, COLOURS[1] is the pixel colour.

class Screen:
    def __init__(self, scale: int=16) -> None:
        self.cols = 64
        self.rows = 32
        self.scale = scale
        self.vram = bytearray(self.cols * self.rows)
        self.surface = pg.display.set_mode((self.cols * self.scale,
            self.rows * self.scale), pg.HWSURFACE|pg.DOUBLEBUF|pg.RESIZABLE)

        self.clear()

    def prepare_frame(self, framebuffer) -> None:
        # prepare to draw the next frame given by the framebuffer
        pass

    def draw_pixel(self, x: int, y: int, colour: int) -> None:
        coords = pg.Rect(x * self.scale, y * self.scale, self.scale, self.scale)
        self.surface.fill(COLOURS[colour], coords)

    def get_pixel(self, x: int, y: int) -> int:
        pixel = self.surface.get_at((x * self.scale, y * self.scale))
        if pixel == COLOURS[0]:
            colour = 0
        else:
            colour = 1
        return colour

    def clear(self):
        self.surface.fill(COLOURS[0])

    @staticmethod
    def update_frame() -> None:
        """
        Paint a new frame
        """
        pg.display.flip()

    @staticmethod
    def quit():
        pg.display.quit()
    