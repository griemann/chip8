
import pygame as pg
import sys
import time

from cpu import CPU

def main(rom_path):
    pg.init()
    # initialize cpu
    cpu = CPU()

    rom = open(rom_path, 'rb')
    rom_bytes = rom.read()
    rom.close()

    cpu.load_rom(rom_bytes)

    t = 0
    while True:
        print(cpu)

        t = time.time()
        cpu.exec()

        dt = time.time() - t
        if dt < 1/60:
            time.sleep(1/60 - dt)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('./roms/test_opcode.ch8')

    pg.quit()
    