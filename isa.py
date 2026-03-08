

registers = {
    # ABI names 
    "zero": "00000",  # x0  - Hard-wired zero
    "ra":   "00001",  # x1  - Return address
    "sp":   "00010",  # x2  - Stack pointer
    "gp":   "00011",  # x3  - Global pointer
    "tp":   "00100",  # x4  - Thread pointer
    "t0":   "00101",  # x5  - Temporary
    "t1":   "00110",  # x6  - Temporary
    "t2":   "00111",  # x7  - Temporary
    "s0":   "01000",  # x8  - Saved / frame pointer
    "fp":   "01000",  # x8  - alias for s0
    "s1":   "01001",  # x9  - Saved register
    "a0":   "01010",  # x10 - Arg / return value
    "a1":   "01011",  # x11 - Arg / return value
    "a2":   "01100",  # x12 - Argument
    "a3":   "01101",  # x13 - Argument
    "a4":   "01110",  # x14 - Argument
    "a5":   "01111",  # x15 - Argument
    "a6":   "10000",  # x16 - Argument
    "a7":   "10001",  # x17 - Argument
    "s2":   "10010",  # x18 - Saved register
    "s3":   "10011",  # x19 - Saved register
    "s4":   "10100",  # x20 - Saved register
    "s5":   "10101",  # x21 - Saved register
    "s6":   "10110",  # x22 - Saved register
    "s7":   "10111",  # x23 - Saved register
    "s8":   "11000",  # x24 - Saved register
    "s9":   "11001",  # x25 - Saved register
    "s10":  "11010",  # x26 - Saved register
    "s11":  "11011",  # x27 - Saved register
    "t3":   "11100",  # x28 - Temporary
    "t4":   "11101",  # x29 - Temporary
    "t5":   "11110",  # x30 - Temporary
    "t6":   "11111",  # x31 - Temporary

    # x-number aliases
    "x0":  "00000", "x1":  "00001", "x2":  "00010", "x3":  "00011",
    "x4":  "00100", "x5":  "00101", "x6":  "00110", "x7":  "00111",
    "x8":  "01000", "x9":  "01001", "x10": "01010", "x11": "01011",
    "x12": "01100", "x13": "01101", "x14": "01110", "x15": "01111",
    "x16": "10000", "x17": "10001", "x18": "10010", "x19": "10011",
    "x20": "10100", "x21": "10101", "x22": "10110", "x23": "10111",
    "x24": "11000", "x25": "11001", "x26": "11010", "x27": "11011",
    "x28": "11100", "x29": "11101", "x30": "11110", "x31": "11111",
}

instructions = {
    #R-type
    "add":   {"type": "R", "opcode": "0110011", "f3": "000", "f7": "0000000"},
    "sub":   {"type": "R", "opcode": "0110011", "f3": "000", "f7": "0100000"},
    "sll":   {"type": "R", "opcode": "0110011", "f3": "001", "f7": "0000000"},
    "slt":   {"type": "R", "opcode": "0110011", "f3": "010", "f7": "0000000"},
    "sltu":  {"type": "R", "opcode": "0110011", "f3": "011", "f7": "0000000"},
    "xor":   {"type": "R", "opcode": "0110011", "f3": "100", "f7": "0000000"},
    "srl":   {"type": "R", "opcode": "0110011", "f3": "101", "f7": "0000000"},
    "or":    {"type": "R", "opcode": "0110011", "f3": "110", "f7": "0000000"},
    "and":   {"type": "R", "opcode": "0110011", "f3": "111", "f7": "0000000"},

    #I-type 
    "lw":    {"type": "I", "opcode": "0000011", "f3": "010"},
    "addi":  {"type": "I", "opcode": "0010011", "f3": "000"},
    "sltiu": {"type": "I", "opcode": "0010011", "f3": "011"},
    "jalr":  {"type": "I", "opcode": "1100111", "f3": "000"},

    #S-type
    "sw":    {"type": "S", "opcode": "0100011", "f3": "010"},

    #B-type
    "beq":   {"type": "B", "opcode": "1100011", "f3": "000"},
    "bne":   {"type": "B", "opcode": "1100011", "f3": "001"},
    "blt":   {"type": "B", "opcode": "1100011", "f3": "100"},
    "bge":   {"type": "B", "opcode": "1100011", "f3": "101"},
    "bltu":  {"type": "B", "opcode": "1100011", "f3": "110"},
    "bgeu":  {"type": "B", "opcode": "1100011", "f3": "111"},

    #U-type
    "lui":   {"type": "U", "opcode": "0110111"},
    "auipc": {"type": "U", "opcode": "0010111"},

    #J-type
    "jal":   {"type": "J", "opcode": "1101111"},

    #Bonus instructions
    "mul":   {"type": "R", "opcode": "0110011", "f3": "000", "f7": "0000001"},
    "rst":   {"type": "BONUS_RST",  "opcode": "0001011", "f3": "000", "f7": "0000000"},
    "halt":  {"type": "BONUS_HALT", "opcode": "0001011", "f3": "001", "f7": "0000000"},
    "rvrs":  {"type": "BONUS_RVRS", "opcode": "0001011", "f3": "010", "f7": "0000000"},
}
