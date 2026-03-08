import sys
from isa import registers, instructions

def pass_one(input_file):
    label_map = {}
    cleaned_instructions = []
    current_pc = 0 

    try:
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.split('#')[0].strip()
                if not clean_line:
                    continue
                
                if ':' in clean_line:
                    label_part, _, instr_part = clean_line.partition(':')
                    label_name = label_part.strip()
                    if label_name:
                        label_map[label_name] = current_pc
                    clean_line = instr_part.strip()

                if clean_line:
                    cleaned_instructions.append((current_pc, clean_line, line_num))
                    current_pc += 4

        if cleaned_instructions:
            last_instr = cleaned_instructions[-1][1].replace(" ", "").lower()
            if "beqzero,zero,0" not in last_instr:
                print("Error: Program must end with beq zero, zero, 0")

        return label_map, cleaned_instructions
    except FileNotFoundError:
        return None, None

def encode_rtype(name, ops):
    info = instructions[name]
    return info["f7"] + registers[ops[2]] + registers[ops[1]] + info["f3"] + registers[ops[0]] + info["opcode"]

def encode_itype(name, ops):
    info = instructions[name]
    if name in ["lw", "jalr"]:
        rd, imm_val, rs1 = ops[0], int(ops[1]), ops[2]
    else:
        rd, rs1, imm_val = ops[0], ops[1], int(ops[2])
    imm = format(imm_val & 0xFFF, '012b')
    return imm + registers[rs1] + info["f3"] + registers[rd] + info["opcode"]

def encode_stype(name, ops):
    info = instructions[name]
    rs2, imm_val, rs1 = registers[ops[0]], int(ops[1]), registers[ops[2]]
    imm = format(imm_val & 0xFFF, '012b')
    return imm[:7] + rs2 + rs1 + info["f3"] + imm[7:] + info["opcode"]

def encode_utype(name, ops):
    info = instructions[name]
    imm = format(int(ops[1]) & 0xFFFFF, '020b')
    return imm + registers[ops[0]] + info["opcode"]

def encode_btype(name, ops, current_pc, label_map):
    info = instructions[name]
    target_pc = label_map[ops[2]]
    offset = target_pc - current_pc
    imm = format(offset & 0x1FFF, '013b')
    return imm[0] + imm[2:8] + registers[ops[1]] + registers[ops[0]] + info["f3"] + imm[8:12] + imm[1] + info["opcode"]

def encode_jtype(name, ops, current_pc, label_map):
    info = instructions[name]
    target_pc = label_map[ops[1]]
    offset = target_pc - current_pc
    imm = format(offset & 0x1FFFFF, '021b')
    return imm[0] + imm[10:20] + imm[9] + imm[1:9] + registers[ops[0]] + info["opcode"]

def pass_two(label_map, instrs):
    output_bin = []
    for pc, line, line_num in instrs:
        clean_line = line.replace(',', ' ').replace('(', ' ').replace(')', ' ')
        parts = clean_line.split()
        name, ops = parts[0].lower(), parts[1:]

        try:
            itype = instructions[name].get("type")
            if itype == "R": binary = encode_rtype(name, ops)
            elif itype == "I": binary = encode_itype(name, ops)
            elif itype == "S": binary = encode_stype(name, ops)
            elif itype == "U": binary = encode_utype(name, ops)
            elif itype == "B": binary = encode_btype(name, ops, pc, label_map)
            elif itype == "J": binary = encode_jtype(name, ops, pc, label_map)
            else: continue
            output_bin.append(binary)
        except Exception:
            return None
    return output_bin

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        labels, cleaned_instrs = pass_one(sys.argv[1])
        if labels is not None:
            binary_code = pass_two(labels, cleaned_instrs)
            if binary_code:
                with open(sys.argv[2], 'w') as f:
                    f.write("\n".join(binary_code) + "\n")
