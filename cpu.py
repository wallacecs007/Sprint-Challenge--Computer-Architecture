"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.stack_pointer = 7
        self.flag = 0b00000000

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        try:
            with open(filename) as file:
                for line in file:
                    # Some lines will have a comment after the binary input.
                    # Need to strip that off the end
                    split_comment = line.split('#')
                    value = split_comment[0].strip()
                    if value == "":
                        continue
                    # Converting the string to a number. Have to identify there's
                    # Two bytes using base = 2
                    convert = int(value, 2)
                    self.ram[address] = convert
                    address += 1
        except FileNotFoundError:
            print("File was not found.")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001  # 1 which represents true
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        while self.running:
            instruction_reg = self.ram_read(self.pc)

            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)

            if instruction_reg == 0b10000010:  # LDI
                self.reg[op_a] = op_b
                self.pc += 3

            elif instruction_reg == 0b01000111:  # PRN
                print(self.reg[op_a])
                self.pc += 2

            elif instruction_reg == 0b00000001:  # HTL
                print("The program is now stopping due to a HALT function.")
                self.running = False

            elif instruction_reg == 0b10100010:  # MUL
                self.alu("MUL", op_a, op_b)

            elif instruction_reg == 0b01000110:  # POP
                given_register = self.ram[self.pc + 1]
                value_from_memory = self.ram[self.reg[self.stack_pointer]]
                self.reg[given_register] = value_from_memory
                self.reg[self.stack_pointer] += 1
                self.pc += 2

            elif instruction_reg == 0b01000101:  # PUSH
                given_register = self.ram[self.pc + 1]
                value_in_register = self.reg[given_register]
                self.reg[self.stack_pointer] -= 1
                self.ram[self.reg[self.stack_pointer]] = value_in_register
                self.pc += 2

            elif instruction_reg == 0b10100111:  # CMP
                self.alu('CMP', op_a, op_b)
                self.pc += 3

            elif instruction_reg == 0b01010100:  # JMP
                self.pc = self.reg[op_a]

            elif instruction_reg == 0b01010101:  # JEQ
                if self.flag == 0b00000001:  # 1 which represents true
                    self.pc = self.reg[op_a]
                else:
                    self.pc += 2

            elif instruction_reg == 0b01010110:  # JNE
                if self.flag != 0b00000001:  # 1 which represents true
                    self.pc = self.reg[op_a]
                else:
                    self.pc += 2

            else:
                print(
                    f"Unknown Command: {instruction_reg}. Program is now stopping.")
                self.running = False
                sys.exit(1)
