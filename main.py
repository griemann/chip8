
import pygame as pg
import sys

from cpu import CPU

def main(rom_path):
    pg.init()
    # initialize cpu
    cpu = CPU()

    rom = open(rom_path, 'rb')
    rom_bytes = rom.read()
    rom.close()

    cpu.load_rom(rom_bytes)
    val = 0
    cont = True
    prompt = None
    while True:
        cpu.exec()
        print(cpu)
        val += 1
        #cont = not cont
        while not cont:
            prompt = input()
            if prompt is not None:
                cont = not cont
        prompt = None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('./roms/ibm.ch8')

    pg.quit()
    