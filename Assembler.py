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
