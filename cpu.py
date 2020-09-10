from random import randint

from keyboard import Keyboard
from screen import Screen
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
        # stack pointer, 8-bit. Starts in memory after the sprite data.
        self.sp = 0x52
        self.delay_timer = 0
        self.sound_timer = 0

        self.screen = Screen()
        self.keyboard = Keyboard()

        self.curr_op = 0x00e0
        self.load_sprites()

        self.op_table = {
            0x0: self.clr_ret,
            0x1: self.jump_to_address,
            0x2: self.jump_to_subroutine,
            0x3: self.skip_if_reg_eq_val,
            0x4: self.skip_if_reg_neq_val,
            0x5: self.skip_if_reg_eq_reg,
            0x6: self.load_to_reg,
            0x7: self.add_val_to_reg,
            0x8: self.exec_logical_ops,
            0x9: self.skip_if_reg_neq_reg,
            0xA: self.load_index_reg,
            0xB: self.jump_to_addr_offset,
            0xC: self.gen_random_number,
            0xD: self.draw_sprite,
            0xE: self.keyboard_ops,
            0xF: self.exec_misc_ops
        }

        # ALU operations for when the operand starts with 8.
        # The last hex digit determines which operation to perform.
        self.logical_op_table = {
            0x0: self.load_reg_to_reg,
            0x1: self.logical_or,
            0x2: self.logical_and,
            0x3: self.exclusive_or,
            0x4: self.add_reg_to_reg,
            0x5: self.subtract_reg_from_reg,
            0x6: self.right_shift_reg,
            0x7: self.subtract_reg_from_reg_n,
            0xe: self.left_shift_reg
        }

        self.misc_table = {
            0x07: self.load_delay_val_to_reg,
            0x0A: self.wait_for_key,
            0x15: self.set_delay_timer,
            0x18: self.set_sound_timer,
            0x1e: self.add_to_index,
            0x29: self.load_sprite_to_index,
            0x33: self.store_bcd_in_memory,
            0x55: self.store_regs_in_memory,
            0x65: self.load_regs_from_memory
        }

    def __str__(self) -> str:
        s = 'PC: {:04X}  OP: {:04X}'.format(self.pc - 2, self.curr_op)
        return s

    def load_rom(self, rom: bytes) -> None:
        for i in range(len(rom)):
            self.memory[0x200 + i] = rom[i]

    def load_sprites(self) -> None:
        for i in range(len(SPRITES)):
            self.memory[i] = SPRITES[i]

    def exec(self) -> None:
        """
        Execute the current instruction, then advance the program.
        """
        self.step()
        instruction_bits = (self.curr_op & 0xf000) >> 12
        self.op_table[instruction_bits]()

    def step(self) -> None:
        """
        Fetch next instruction.
        """
        self.curr_op = self.memory[self.pc] << 8
        self.curr_op += self.memory[self.pc + 1]
        self.pc += 2

    def exec_logical_ops(self):
        """
        The opcodes for logical instructions have 0x8 as their
        left-most hex digit.
        """
        operation = self.curr_op & 0x000f
        self.logical_op_table[operation]()

    def exec_misc_ops(self):
        """
        The opcodes for logical instructions have 0xF as their
        left-most hex digit.
        """
        operation = self.curr_op & 0x00ff
        self.misc_table[operation]()

    def clr_ret(self) -> None:
        """
        00E0 - CLS
        Clear the display.
        """
        operation = self.curr_op & 0x00ff

        if operation == 0xe0:
            self.screen.clear()
        elif operation == 0xee:
            self.return_from_subroutine()

    def return_from_subroutine(self) -> None:
        """
        00EE - RET
        Return from a subroutine.  Set program counter to the address at the top
        of the stack, then subtracts 1 from the stack pointer.
        """
        self.sp -= 1
        right_byte = self.memory[self.sp]
        self.sp -= 1
        left_byte = self.memory[self.sp] << 8
        self.pc = left_byte + right_byte

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
        self.memory[self.sp] = (self.pc & 0xff00) >> 8
        self.sp += 1
        self.memory[self.sp] = self.pc & 0x00ff
        self.sp += 1
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

    def load_reg_to_reg(self) -> None:
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

    def load_index_reg(self) -> None:
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
        self.v[0xf] = 0x0

        total_sprite_bytes = self.curr_op & 0x000f
        x_offset = self.v[(self.curr_op & 0x0f00) >> 8]
        y_offset = self.v[(self.curr_op & 0x00f0) >> 4]
        for row_no in range(total_sprite_bytes):
            for col_no in range(8):
                x_target = col_no + x_offset
                y_target = row_no + y_offset

                curr_colour = self.screen.get_pixel(x_target, y_target)
                colour = self.memory[self.i + row_no] >> (7 - col_no)
                colour = colour & 0x1

                if curr_colour and colour:
                    self.v[0xf] = 1

                self.screen.draw_pixel(x_target, y_target, colour ^ curr_colour)
        self.screen.update_frame()

    def keyboard_ops(self) -> None:
        operation = self.curr_op & 0x00FF
        if operation == 0x9e:
            self.skip_if_key_press()
        
        if operation == 0xa1:
            self.skip_if_not_key_press()

    def skip_if_key_press(self) -> None:
        """
        Ex9E - SKP Vx
        Skip next instruction if key with the value of Vx is pressed.
        """
        x = (self.curr_op & 0x0f00) >> 8
        if self.keyboard.is_pressed(x):
            self.pc += 2

    def skip_if_not_key_press(self) -> None:
        """
        ExA1 - SKNP Vx
        Skip next instruction if key with the value of Vx is not pressed.
        """
        x = (self.curr_op & 0x0f00) >> 8
        if not self.keyboard.is_pressed(x):
            self.pc += 2

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
        pressed_key = self.keyboard.is_any_pressed()
        if pressed_key is not None:
            self.v[x] = pressed_key

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

    def load_regs_from_memory(self) -> None:
        """
        Fx65 - LD Vx, [I]
        Read registers V0 through Vx from memory starting at location I.
        """
        x = (self.curr_op & 0x0f00) >> 8
        for n in range(x + 1):
            self.v[n] = self.memory[self.i + n]
