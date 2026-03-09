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
    
def b_type(instr, r1, r2, imm):
    data = instructions[instr]
    imm_bits = convert_to_twos_complement(imm, 13)
    bit12 = imm_bits[0]
    bit11 = imm_bits[1]
    bits_10_5 = imm_bits[2:8]
    bits_4_1 = imm_bits[8:12]
    out = bit12 + bits_10_5 + registers[r2] + registers[r1] + data["f3"] + bits_4_1 + bit11 + data["opcode"]
    return out

def u_type(instr, rd, imm):
    data = instructions[instr]
    imm_bits = convert_to_twos_complement(imm, 20)
    out = imm_bits + registers[rd] + data["opcode"]
    return out

def j_type(instr, rd, imm):
    data = instructions[instr]
    imm_bits = convert_to_twos_complement(imm, 21)
    bit20 = imm_bits[0]
    bits_10_1 = imm_bits[10:20]
    bit11 = imm_bits[9]
    bits_19_12 = imm_bits[1:9]
    out = bit20 + bits_10_1 + bit11 + bits_19_12 + registers[rd] + data["opcode"]
    return out
    
def first_pass(filepath):
    labels = {}
    code_lines = []
    addr = 0
    
    try:
        file = open(filepath, 'r')
        all_lines = file.readlines()
        file.close()
    except:
        print("Error: Could not find file " + filepath)
        return None, None
    
    line_number = 0
    for raw_line in all_lines:
        line_number = line_number + 1
        
        # remove comments
        if '#' in raw_line:
            idx = raw_line.index('#')
            raw_line = raw_line[:idx]
        raw_line = raw_line.strip()
        
        if raw_line == '':
            continue
        
        # handle labels
        if ':' in raw_line:
            colon_pos = raw_line.index(':')
            lbl = raw_line[:colon_pos].strip()
            raw_line = raw_line[colon_pos+1:].strip()
            
            if len(lbl) == 0 or not lbl[0].isalpha():
                print("Error at line " + str(line_number) + ": Label '" + lbl + "' must start with a letter.")
                return None, None
            
            labels[lbl] = addr
        
        if raw_line != '':
            code_lines.append((addr, raw_line, line_number))
            addr = addr + 4
    
    # verify halt exists
    halt_found = False
    for item in code_lines:
        if check_virtual_halt(item[1]):
            halt_found = True
            break
    
    if not halt_found:
        print("Error: Program must contain Virtual Halt (beq zero, zero, 0)")
        return None, None
    
    # verify halt is last
    if len(code_lines) > 0:
        final_instr = code_lines[-1][1]
        if not check_virtual_halt(final_instr):
            print("Error: Virtual Halt must be the last instruction")
            return None, None
    
    return labels, code_lines

def assemble(labels, code_lines, outfile):
    machine_code = []
    
    for entry in code_lines:
        addr = entry[0]
        instr_text = entry[1]
        ln = entry[2]
        
        # normalize
        temp = instr_text.replace(',', ' ').replace('(', ' ').replace(')', ' ')
        temp = temp.lower()
        tokens = temp.split()
        
        opname = tokens[0]
        args = tokens[1:]
        
        try:
            result = None
            
            # R-type
            if opname in ["add", "sub", "slt", "sltu", "xor", "sll", "srl", "or", "and"]:
                result = r_type(opname, args[0], args[1], args[2])
            
            # I-type arithmetic
            elif opname == "addi" or opname == "sltiu":
                imm_val = int(args[2], 0)
                result = i_type(opname, args[0], args[1], imm_val)
            
            # load word
            elif opname == "lw":
                imm_val = int(args[1], 0)
                result = i_type(opname, args[0], args[2], imm_val)
            
            # store word
            elif opname == "sw":
                imm_val = int(args[1], 0)
                result = s_type(opname, args[0], args[2], imm_val)
            # branches
            elif opname in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
                if args[2] in labels:
                    offset = labels[args[2]] - addr
                else:
                    offset = int(args[2], 0)
                result = b_type(opname, args[0], args[1], offset)
            
            # upper immediate
            elif opname == "lui" or opname == "auipc":
                imm_val = int(args[1], 0)
                result = u_type(opname, args[0], imm_val)
            
            # jump and link
            elif opname == "jal":
                if args[1] in labels:
                    offset = labels[args[1]] - addr
                else:
                    offset = int(args[1], 0)
                result = j_type(opname, args[0], offset)
            
            # jump and link register
            elif opname == "jalr":
                if args[1] in registers:
                    imm_val = int(args[2], 0)
                    result = i_type(opname, args[0], args[1], imm_val)
                else:
                    imm_val = int(args[1], 0)
                    result = i_type(opname, args[0], args[2], imm_val)
            
            else:
                print("Error at line " + str(ln) + ": Unknown instruction " + opname)
                sys.exit(1)
            
            machine_code.append(result)
            
        except Exception as err:
            print("Error at line " + str(ln) + ": " + str(err))
            sys.exit(1)
    
    # write output
    f = open(outfile, 'w')
    for code in machine_code:
        f.write(code + "\n")
    f.close()
            
