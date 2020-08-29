import pygame as pg
from random import randint
from sprites import SPRITES

class CPU:
    def __init__(self) -> None:
        self.memory = bytearray(4096)
        # general purpose registers, 16 in total, each 8-bit
        self.v = bytearray(0x10)
        # index register, 16-bit
        self.i = 0x0000
        # program counter, 16-bit
        self.pc = 0x0200
        # stack pointer, 8-bit
        self.sp = 0x00
        # the stack holds 16 16-bit values
        self.stack = bytearray(16 * 2)
        self.delay_timer = 0
        self.sound_timer = 0

        self.curr_op = 0x00e0

    def load_rom(self, rom: bytes) -> None:
        for i in range(len(bytes)):
            self.memory[0x200 + i] = rom[i]

    def load_sprites(self) -> None:
        for i in range(len(SPRITES)):
            self.memory[i] = SPRITES[i]

    def exec(self) -> None:
        """
        Execute the current instruction, then advance the program.
        """
        pass
        self.step()

    def step(self) -> None:
        """
        Fetch next instruction.
        """
        self.curr_op = self.memory[self.pc] << 8
        self.curr_op = self.curr_op & self.memory[self.pc + 1]
        self.pc += 2

    def clr(self) -> None:
        """
        00E0 - CLS
        Clear the display.
        """
        operation = self.curr_op & 0x00ff

        if operation == 0xe0:
            # clear display
            pass
        elif operation == 0xee:
            # return
            pass

    def return_from_subroutine(self) -> None:
        """
        00EE - RET
        Return from a subroutine.  Set program counter to the address at the top
        of the stack, then subtracts 1 from the stack pointer.
        """
        self.sp -= 1
        self.pc = self.stack[self.sp]
        self.sp -= 1
        self.pc = self.pc & (self.stack[self.sp] << 8)

    def jump_to_address(self) -> None:
        """
        1nnn - JP addr
        Set the program counter to nnn.
        """
        self.pc = self.curr_op & 0x0fff

    def jump_to_subroutine(self) -> None:
        """
        2nnn - CALL addr
        Call subroutine at nnn.

        Increment the stack pointer, then put the current PC on the top of the 
        stack. The PC is then set to nnn.
        """
        self.sp += 2
        self.stack[self.sp] = self.pc
        self.pc = self.curr_op & 0x0fff

    def skip_if_reg_eq_val(self) -> None:
        """
        3xkk - SE Vx, byte
        Skip next instruction if Vx = kk.
        """
        x = (self.curr_op & 0x0f00) >> 8
        val = self.curr_op & 0x00ff

        if self.v[x] == val:
            self.pc += 2
    
    def skip_if_reg_neq_val(self) -> None:
        """
        4xkk - SNE Vx, byte
        Skip next instruction if Vx != kk.
        """
        x = (self.curr_op & 0x0f00) >> 8
        val = self.curr_op & 0x00ff

        if self.v[x] != val:
            self.pc += 2

    def skip_if_reg_eq_reg(self) -> None:
        """
        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy.
        """
        x = (self.curr_op & 0x0f00) >> 8
        y = (self.curr_op & 0x00f0) >> 4

        if self.v[x] == self.v[y]:
            self.pc += 2

    def load_to_reg(self) -> None:
        """
        6xkk - LD Vx, byte
        Set Vx = kk.
        """
        x = (self.curr_op & 0x0f00) >> 8
        val = self.curr_op & 0x00ff
        self.v[x] = val

    def add_val_to_reg(self) -> None:
        """
        7xkk - ADD Vx, byte
        Set Vx = Vx + kk.
        """
        x = (self.curr_op & 0x0f00) >> 8
        val = self.curr_op & 0x00ff
        # we take mod 256 since the value stored is 8-bit only
        self.v[x] = (self.v[x] + val) % 256

    def copy_reg(self) -> None:
        """
        8xy0 - LD Vx, Vy
        Set Vx = Vy.
        """
        x = (self.curr_op & 0x0f00) >> 8
        y = (self.curr_op & 0x00f0) >> 4
        self.v[x] = self.v[y]

    def logical_or(self) -> None:
        """
        8xy1 - OR Vx, Vy
        Set Vx = Vx OR Vy.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4
        self.v[x] |= self.v[y]

    def logical_and(self) -> None:
        """
        8xy2 - AND Vx, Vy
        Set Vx = Vx AND Vy.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4
        self.v[x] &= self.v[y]

    def exclusive_or(self) -> None:
        """
        8xy3 - XOR Vx, Vy
        Set Vx = Vx XOR Vy.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4
        self.v[x] ^= self.v[y]

    def add_reg_to_reg(self) -> None:
        """
        8xy4 - ADD Vx, Vy
        Set Vx = Vx + Vy, set VF = carry.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4
        self.v[x] += self.v[y]
        
        if self.v[x] > 255:
            self.v[x] = self.v[x] % 256
            self.v[0xf] = 1

    def subtract_reg_from_reg(self) -> None:
        """
        8xy5 - SUB Vx, Vy
        Set Vx = Vx - Vy, set VF = NOT borrow.
        If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from
        Vx, and the results stored in Vx.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4

        if self.v[x] > self.v[y]:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0
        
        self.v[x] = (self.v[x] - self.v[y]) % 256

    def right_shift_reg(self) -> None:
        """
        8xy6 - SHR Vx, Vy
        Set Vx = Vx SHR 1. Store the shifted bit in VF
        """
        x = (self.curr_op & 0x0f00) >> 8
        self.v[0xf] = self.v[x] & 0x1
        self.v[x] = self.v[x] >> 1

    def subtract_reg_from_reg_n(self) -> None:
        """
        8xy7 - SUBN Vx, Vy
        Set Vx = Vy - Vx, set VF = NOT borrow.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4

        if self.v[y] > self.v[x]:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0

        self.v[x] = (self.v[y] - self.v[x]) % 256

    def left_shift_reg(self) -> None:
        """
        8xyE - SHL Vx, Vy
        Set Vx = Vx SHL 1. Store the shifted bit in VF
        """
        x = (self.curr_op & 0x0f00) >> 8
        self.v[0xf] = self.v[0xf] & 0b10000000
        self.v[x] = self.v[x] << 1

    def skip_if_reg_neq_reg(self) -> None:
        """
        9xy0 - SNE Vx, Vy
        Skip next instruction if Vx != Vy.
        """
        x = (self.curr_op & 0x0f00) >> 8 
        y = (self.curr_op & 0x00f0) >> 4

        if self.v[x] != self.v[y]:
            self.pc += 2

    def set_index_reg(self) -> None:
        """
        Annn - LD I, addr
        Set I = nnn.
        """
        self.i = self.curr_op & 0x0fff

    def jump_to_addr_offset(self) -> None:
        """
        Bnnn - JP V0, addr
        Jump to location nnn + V0.
        """
        val = self.curr_op & 0x0fff
        self.pc = val + self.v[0x0]

    def gen_random_number(self) -> None:
        """
        Cxkk - RND Vx, byte
        Set Vx = random byte AND kk.
        """
        x = (self.curr_op & 0x0f00) >> 8
        val = self.curr_op & 0x00ff
        self.v[x] = val & randint(0, 0xff)

    def draw_sprite(self) -> None:
        """
        Dxyn - DRW Vx, Vy, nibble
        Display n-byte sprite starting at memory location I at (Vx, Vy),
        set VF = collision.
        """
        pass

    def skip_if_key_press(self) -> None:
        """
        Ex9E - SKP Vx
        Skip next instruction if key with the value of Vx is pressed.
        """
        pass

    def skip_if_not_key_press(self) -> None:
        """
        ExA1 - SKNP Vx
        Skip next instruction if key with the value of Vx is not pressed.
        """
        pass

    def load_delay_val_to_reg(self) -> None:
        """
        Fx07 - LD Vx, DT
        Set Vx = delay timer value.
        """
        x = (self.curr_op & 0x0f00) >> 8
        self.v[x] = self.delay_timer

    def wait_for_key(self) -> None:
        """
        Fx0A - LD Vx, K
        Wait for a key press, store the value of the key in Vx.
        """
        x = (self.curr_op & 0x0f00) >> 8
        pass

    def set_delay_timer(self) -> None:
        """
        Fx15 - LD DT, Vx
        Set delay timer = Vx.
        """
        x = (self.curr_op & 0x0f00) >> 8
        self.delay_timer = self.v[x]

    def set_sound_timer(self) -> None:
        """
        Fx18 - LD ST, Vx
        Set sound timer = Vx.
        """
        x = (self.curr_op & 0x0f00) >> 8
        self.sound_timer = self.v[x]

    def add_to_index(self) -> None:
        """
        Fx1E - ADD I, Vx
        Set I = I + Vx.
        """
        x = (self.curr_op & 0x0f00) >> 8
        self.i += self.v[x]

    def load_sprite_to_index(self) -> None:
        """
        Fx29 - LD F, Vx
        Set I = location of sprite for digit Vx.
        """
        x = (self.curr_op & 0x0f00) >> 8
        # each sprite is 5 bytes
        self.i = self.memory[self.v[x] * 5]

    def store_bcd_in_memory(self) -> None:
        """
        Fx33 - LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, and I+2.
        """
        x = (self.curr_op & 0x0f00) >> 8
        decimal_str = '{:03d}'.format(self.v[x])
        self.memory[self.i] = int(decimal_str[0]) # hundreds
        self.memory[self.i + 1] = int(decimal_str[1])
        self.memory[self.i + 2] = int(decimal_str[2])

    def store_regs_in_memory(self) -> None:
        """
        Fx55 - LD [I], Vx
        Store registers V0 through Vx in memory starting at location I.
        """
        x = (self.curr_op & 0x0f00) >> 8
        for n in range(x + 1):
            self.memory[self.i + n] = self.v[n]
        
    def read_regs_from_memory(self) -> None:
        """
        Fx65 - LD Vx, [I]
        Read registers V0 through Vx from memory starting at location I.
        """
        x = (self.curr_op & 0x0f00) >> 8
        for n in range(x + 1):
            self.v[n] = self.memory[self.i + n]