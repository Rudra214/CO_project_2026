#We have used comments so that our team members can easily understand what each line of code is doing.
import sys
from isa import registers,instructions

def pass_one(input_file):
    label_map = {}
    cleaned_instructions = {}
    current_pc = 0  #Here we are initialising the program counter to 0 intially.

    try:
        with open(input_file,'r') as f:
            lines = f.readlines()

        for line_num,line in enumerate(lines,1):
            clean_line = line.strip()  #Here I am basically asking it to skip any empty lines
            if not clean_line or clean_line.startswith('#'):  #Here we basically continue reading if we dont encounter an empty line or comment
                continue
        
            if ':' in clean_line:
                label_part, _ , instr_part = clean_line.partition(':')
                label_name = label_part.strip() #Here if we find a colon in a line we basically split the command into the label and other part like LOOP,etc
        
                if not label_name[0].isalpha():
                    print(f"Error at line {line_num}: Label '{label_name}' must start with a character.")
            #Here we check the first character in the label name.If we have something like _LOOP: it gives out an error as first character isnt an alphabet.

                label_map[label_name] = current_pc
                clean_line = instr_part.strip()  #Now we basically remove the label part of the instruction and proceed to the next part after saving the label.

            
            if clean_line:
                cleaned_instructions.append((current_pc,clean_line,line_num))
                current_pc +=4    #Here we make a tuple with information regarding current_pc,clean_line and the line_num after which we update the pc. 

        if cleaned_instructions:
            last_instr = cleaned_instructions[-1][1]  #Here we check the last and second element of the tuple to check if it is empty.
            if "beq,zero,zero,0" not in last_instr.replace(" ",""): 
                print("Error: Program must end with Virtual Halt (beq zero,zero,0).")

            return label_map, cleaned_instructions
    
    except FileNotFoundError:
        print(f"Error: Could not find file {input_file}")
        return None,None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 assembler.py input.asm output.bin")
    else:
        labels, instrs = pass_one(sys.argv[1])
        if labels is not None:
            print(f"First Pass complete. Found {len(labels)} labels.")



#now we will start with the r-type encoding

def encode_rtype(instruction, rd, rs1, rs2):
    info = instructions [instruction]

    funct7 = info["f7"]
    funct3 = info["f3"]
    opcode = info["opcode"]

    rd_binary = registers[rd]
    rs1_binary = registers[rs1]
    rs2_binary = registers[rs2]

    binary = funct7 + rs2_binary + rs1_binary + funct3 + rd_binary + opcode

    return binary

#test
if __name__ == "__main__":
	print("\nR-Type encoder test below")
	result = encode_rtype("add", "s1", "s2", "s3")
	print("add s1, s2, s3 =", result)


#below is the implementation of i-type encoding

def encode_itype(name, operands, instructions, registers):
    
    #checking if the instruction name is present in instruction mapping
    if name not in instructions:
        return f"Error: unknown instruction '{name}'"

    info = instructions[name]

    #I-type need 3 operands: rd, rs1, imm
    if len(operands) != 3:
        return f"Error: '{name}' needs 3 operands "

    try:

        rd = registers[operands[0]]

        #for jalr and lw: syntax is rd, offset(rs1) -> operands: [rd, offset, rs1]
        if name in ["lw", "jalr"]:
            imm_val = int(operands[1])
            rs1 = registers[operands[2]]

        #for addi, sltiu: syntax is rd, rs1, imm -> operands: [rd, rs1, imm]
        else:
            rs1 = registers[operands[1]]
            imm_val = int(operands[2])

        
        #checking for immediate range
        if imm_val > 2047 or imm_val < -2048:
            return "Error: immediate out of range"

        imm = format(imm_val & 0xFFF, '012b')

        binarycode = imm + rs1 + info["f3"] + rd + info["opcode"]

        return binarycode

    except ValueError:
        return "Error: invalid immediate value"
    except KeyError:
        return "Error: invalid register"

#test

if __name__ == "__main__":



    print("ErrorGen Tests")

    print("\nErrorGen Tests of I-type")

    print(encode_itype("addi", ["s1","s2"], instructions, registers)) #testing for wrong operand count
    print(encode_itype("sltiu", ["x99", "s2", "10"], instructions, registers)) #testing for invalid registor name

    print("\nSimpleBin Tests")
    r1 = encode_itype("sltiu", ["s1", "s2", "10"], instructions, registers) #checking arithmetic syntax
print("sltiu s1, s2, 10 =", r1)

r2 = encode_itype("jalr", ["ra", "0", "zero"], instructions, registers) #checking load-style syntax
print("jalr ra, 0(zero) =", r2)

print("\nHardGen Test")
r3 = encode_itype("addi", ["t0", "t1", "-2048"], instructions, registers) # checks for maximum negative 12 bit value
print("addi t0, t1, -2048 =", r3)


#next is U- type instructions
def encode_utype(instruction, rd, imm):
	info = instructions[instruction]
	opcode = info["opcode"] #looks up the opcode for the 2 diff instructions it can take --- lui or auipc

	rd_binary = registers[rd] #register name is converted to 5 bit binary

	imm_binary = format(imm, '020b')  #this takes the imm number and converts to binary padded with 0s to make it 20 sigits

	binary = imm_binary + rd_binary + opcode

	return binary

#test

print ("\nU-Type encoder test below")
print ("lui s1, 100 =", encode_utype('lui', 's1', 100))



# code for the s-type instruction

def encode_stype(name, operands, instructions, registers):
	
    #checking if the instruction name is present in instruction mapping
    if name not in instructions:
        return f"Error: unknown instruction '{name}'"

    info = instructions[name]

    #s-type require 3 operands
    if len(operands) != 3:		
        return f"Errror: '{name}' needs 3 operands "

    try:
        rs2 = registers[operands[0]]
        imm_val = int(operands[1])
        rs1 = registers[operands[2]]

        if imm_val < -2048 or imm_val > 2047:
            return "Error: immediate out of range"

	# convert immediate to binary
        imm = format(imm_val & 0xFFF, '012b')

        # split immediate for S-type format
        imm_high = imm[:7]   # imm[11:5]
        imm_low = imm[7:]    # imm[4:0]


        binarycode = imm_high + rs2 + rs1 + info["f3"] + imm_low + info["opcode"]

        return binarycode

    except KeyError:
        return "Error: invalid register"
    except ValueError:
        return "Error: invalid immediate value"

if __name__ == "__main__":

    print("\nErrorGen Tests of S-type instruction")
    print(encode_stype("sw", ["s1", "8"], instructions, registers))
    print(encode_stype("sw", ["x99", "8", "s2"], instructions, registers))

    print("\nSimpleBin Tests")
    r1 = encode_stype("sw", ["s1", "8", "s2"], instructions, registers)
print("sw s1, 8(s2) =", r1)

r2 = encode_stype("sw", ["t0", "16", "sp"], instructions, registers)
print("sw t0, 16(sp) =", r2)

print("\nHardGen Test")
r3 = encode_stype("sw", ["t1", "-2048", "sp"], instructions, registers)
print("sw t1, -2048(sp) =", r3)


#now we will start with j-type encoding

def encode_jtype(instruction, rd, immediate):
    information=instructions[instruction]
    opcode=information["opcode"]
    rd_binary=registers[rd]
    imm=format(int(immediate)&0x1FFFFF, "021b")

    imm_20=imm[0]
    imm_10_1=imm[10:20]
    imm_11=imm[9]
    imm_19_12=imm[1:9]
    
    binary=imm_20+imm_10_1+imm_11+imm_19_12+rd_binary+opcode
    return binary

#code for b-type encoding
def encode_btype(instruction, rd, rs1, rs2, immediate):
	information=instructions[instruction]
	opcode=information["opcode"]
	f3=information["f3"]
	bin_rs1=registers[rs1]
	bin_rs2=registers[rs2]

	imm=format(int(immediate) &  0x1FFF, '013B')
	imm_12=imm[0]
	imm_11=imm[1]
	imm_10_5=imm[2:8]
	imm_4_1=imm[4:12]
	binary=imm_12+imm_10_5+bin_rs2+bin_rs1+f3+imm_4_1+imm_11+opcode
	return binary
	











