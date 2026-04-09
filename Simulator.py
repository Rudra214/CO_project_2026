
import sys

PROG_MEM_START  = 0x00000000
PROG_MEM_END    = 0x000000FF   

STACK_MEM_START = 0x00000100
STACK_MEM_END   = 0x0000017F  
STACK_INIT_SP   = 0x0000017C

DATA_MEM_START  = 0x00010000
DATA_MEM_END    = 0x0001007F   

WORD_MASK = 0xFFFFFFFF
SIGN_BIT  = 0x80000000

#helper function
def to_signed32(val):
    val = val & WORD_MASK
    if val & SIGN_BIT:
        val -= (1 << 32)
    return val

def to_unsigned32(val):
    return val & WORD_MASK

def sign_extend(val, bits):
    """Sign-extend an unsigned integer from 'bits' width to 32 bits."""
    if val & (1 << (bits - 1)):
        val -= (1 << bits)
    return val

def int_to_bin32(val):
    """Return a 32-char binary string (no prefix) for a value."""
    return format(val & WORD_MASK, '032b')

def fmt_reg(val):
    return '0b' + int_to_bin32(val)

def fmt_pc(val):
    return '0b' + format(val & WORD_MASK, '032b')

def fmt_mem_addr(addr):
    return '0x' + format(addr, '08X')

# simulator

class Simulator:
    def __init__(self):

        self.regs = [0] * 32
        self.regs[2] = STACK_INIT_SP   

        self.pc = 0

        self.imem = []

        self.dmem = {}

        self.trace_lines = [] 
        self.halted = False

    def load(self, filepath):
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: could not open {filepath}")
            sys.exit(1)

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if len(line) != 32 or not all(c in '01' for c in line):
                print(f"Error at line {i+1}: invalid instruction '{line}'")
                sys.exit(1)
            self.imem.append(int(line, 2))
    def write_reg(self, rd, val):
        if rd != 0:
            self.regs[rd] = to_unsigned32(val)

    def mem_read(self, addr):
        addr = addr & WORD_MASK
        addr = addr & ~3
        return self.dmem.get(addr, 0)

    def mem_write(self, addr, val):
        addr = addr & WORD_MASK
        addr = addr & ~3
        self.dmem[addr] = to_unsigned32(val)

    # Decode helpers 
    @staticmethod
    def bits(instr, hi, lo):
        mask = (1 << (hi - lo + 1)) - 1
        return (instr >> lo) & mask

    def decode_and_execute(self, instr):
        opcode = self.bits(instr, 6, 0)
        rd     = self.bits(instr, 11, 7)
        funct3 = self.bits(instr, 14, 12)
        rs1    = self.bits(instr, 19, 15)
        rs2    = self.bits(instr, 24, 20)
        funct7 = self.bits(instr, 31, 25)

        pc_next = self.pc + 4   # default

        #R-type: opcode 0110011
        if opcode == 0b0110011:
            a = to_signed32(self.regs[rs1])
            b = to_signed32(self.regs[rs2])
            ua = self.regs[rs1]
            ub = self.regs[rs2]

            if funct3 == 0b000:
                if funct7 == 0b0000000:   # add
                    self.write_reg(rd, ua + ub)
                elif funct7 == 0b0100000: # sub
                    self.write_reg(rd, ua - ub)
            elif funct3 == 0b001:         # sll
                shamt = ub & 0x1F
                self.write_reg(rd, ua << shamt)
            elif funct3 == 0b010:         # slt
                self.write_reg(rd, 1 if a < to_signed32(ub) else 0)
            elif funct3 == 0b011:         # sltu
                self.write_reg(rd, 1 if ua < ub else 0)
            elif funct3 == 0b100:         # xor
                self.write_reg(rd, ua ^ ub)
            elif funct3 == 0b101:         # srl
                shamt = ub & 0x1F
                self.write_reg(rd, ua >> shamt)
            elif funct3 == 0b110:         # or
                self.write_reg(rd, ua | ub)
            elif funct3 == 0b111:         # and
                self.write_reg(rd, ua & ub)

        #I-type arithmetic: opcode 0010011 
        elif opcode == 0b0010011:
            imm = sign_extend(self.bits(instr, 31, 20), 12)
            ua  = self.regs[rs1]
            a   = to_signed32(ua)

            if funct3 == 0b000:           # addi
                self.write_reg(rd, a + imm)
            elif funct3 == 0b011:         # sltiu  (unsigned compare)
                uimm = imm & WORD_MASK
                self.write_reg(rd, 1 if ua < uimm else 0)

        # Load: opcode 0000011 
        elif opcode == 0b0000011:
            imm  = sign_extend(self.bits(instr, 31, 20), 12)
            addr = to_unsigned32(self.regs[rs1] + imm)
            if funct3 == 0b010:           # lw
                val = self.mem_read(addr)
                self.write_reg(rd, val)

        # Store: opcode 0100011 
        elif opcode == 0b0100011:
            imm_hi = self.bits(instr, 31, 25)
            imm_lo = self.bits(instr, 11, 7)
            imm    = sign_extend((imm_hi << 5) | imm_lo, 12)
            addr   = to_unsigned32(self.regs[rs1] + imm)
            if funct3 == 0b010:           # sw
                self.mem_write(addr, self.regs[rs2])

        #Branch: opcode 1100011 
        elif opcode == 0b1100011:
            b12  = self.bits(instr, 31, 31)
            b10_5 = self.bits(instr, 30, 25)
            b4_1  = self.bits(instr, 11, 8)
            b11   = self.bits(instr, 7, 7)
            imm_raw = (b12 << 12) | (b11 << 11) | (b10_5 << 5) | (b4_1 << 1)
            imm = sign_extend(imm_raw, 13)

            a  = to_signed32(self.regs[rs1])
            b  = to_signed32(self.regs[rs2])
            ua = self.regs[rs1]
            ub = self.regs[rs2]

            taken = False
            if funct3 == 0b000:   taken = (a == b)    # beq
            elif funct3 == 0b001: taken = (a != b)    # bne
            elif funct3 == 0b100: taken = (a < b)     # blt
            elif funct3 == 0b101: taken = (a >= b)    # bge
            elif funct3 == 0b110: taken = (ua < ub)   # bltu
            elif funct3 == 0b111: taken = (ua >= ub)  # bgeu

            # Virtual halt check: beq x0, x0, 0
            if funct3 == 0b000 and rs1 == 0 and rs2 == 0 and imm == 0:
                self.halted = True
                pc_next = self.pc
            elif taken:
                pc_next = to_unsigned32(self.pc + imm)

        #LUI: opcode 0110111 
        elif opcode == 0b0110111:
            imm = self.bits(instr, 31, 12) << 12
            self.write_reg(rd, imm)

        #AUIPC: opcode 0010111 
        elif opcode == 0b0010111:
            imm = self.bits(instr, 31, 12) << 12
            self.write_reg(rd, to_unsigned32(self.pc + imm))

    
