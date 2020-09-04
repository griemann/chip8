#!/bin/python3
import pygame as pg
import sys

from cpu import CPU

def main(rom_path):
    # initialize cpu
    cpu = CPU()

    rom = open(rom_path, 'rb')
    rom_bytes = rom.read()
    rom.close()

    cpu.load_rom(rom_bytes)
    



if __name__ == '__main__':
    main(sys.argv[1])