#!/bin/python3

import sys

def get_bytes(rom) -> list:
    pass

def disassemble(rom) -> None:
    mem = 0
    s = ''
    inst = rom.read(2)
    while inst:
        s = '{:04x}: \t {:04x}'.format(mem, int.from_bytes(inst, 'big'))
        mem += 1
        print(s)
        inst = rom.read(2)

if __name__ == '__main__':
    rom_path = sys.argv[1]
    rom = open(rom_path, 'rb')
    disassemble(rom)
    rom.close()
