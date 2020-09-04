import pygame as pg

BLACK = (0x00, 0x00, 0x00)
WHITE = (0xFF, 0xFF, 0xFF)

class Screen:
    def __init__(self, scale: int=1) -> None:
        self.cols = 64
        self.rows = 32
        self.scale = scale
        self.window = pg.display.set_mode((self.cols * self.scale, self.rows * self.scale))
        self.content = pg.Surface(window.get_size())

        self.content.fill((0, 0, 0)) # black background
        self.content.blit(0, 0)

    def prepare_frame(self, framebuffer) -> None:
        # prepare to draw the next frame given by the framebuffer
        pass

    def draw_pixel(self, x: int, y: int) -> None:
        coords = pg.Rect(x, y, self.scale, self.scale)
        self.content.fill(WHITE, coords)

    def draw(self) -> None:
        """
        Draw a new frame.
        """
        self.screen.blit(self.content, (0, 0))