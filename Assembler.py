import sys
from isa import registers, instructions

def convert_to_twos_complement(num, width):
    if num < 0:
        num = num & ((1 << width) - 1)
    return bin(num)[2:].zfill(width)

def check_virtual_halt(line):
    line = line.split('#')[0]
    line = line.replace(',', ' ').replace('(', ' ').replace(')', ' ').lower()
    parts = line.split()
    if len(parts) != 4:
        return False
    if parts[0] != 'beq':
        return False
    if parts[1] not in {'zero', 'x0'} or parts[2] not in {'zero', 'x0'}:
        return False
    try:
        val = int(parts[3], 0)
        return val == 0
    except:
        return False

def r_type(instr, rd, r1, r2):
    data = instructions[instr]
    out = data["f7"] + registers[r2] + registers[r1] + data["f3"] + registers[rd] + data["opcode"]
    return out

def i_type(instr, rd, r1, imm):
    data = instructions[instr]
    imm_bits = convert_to_twos_complement(imm, 12)
    out = imm_bits + registers[r1] + data["f3"] + registers[rd] + data["opcode"]
    return out

def s_type(instr, r2, r1, imm):
    data = instructions[instr]
    imm_bits = convert_to_twos_complement(imm, 12)
    upper = imm_bits[:7]
    lower = imm_bits[7:]
    out = upper + registers[r2] + registers[r1] + data["f3"] + lower + data["opcode"]
    return out
