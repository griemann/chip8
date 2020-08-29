import pygame as pg

class Screen:
    def __init__(self, scale: int = 1) -> None:
        self.cols = 64
        self.rows = 32
        self.scale = scale
        self.window = pg.display.set_mode((self.cols * self.scale, self.rows * self.scale))
        self.content = pg.Surface(window.get_size())

        self.content.fill((0, 0, 0))
        self.content.blit(0, 0)

    def update(mem) -> None:
        # copy the video memory to the screen buffer to prepare the next frame.
        pass

    def draw() -> None:
        """
        Draw a new frame.
        """
        self.screen.blit(self.content, (0, 0))


