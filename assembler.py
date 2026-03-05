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
	result = encode_rtype("add", "s1", "s2", "s3")
	print("add s1, s2, s3 =", result)


#below is the implementation of i-type encoding

def encode_itype(name, operands, instructions, registers):
	
	#checking if the instruction name is present in instruction mapping
	if name not in instructions:
		return f"Error: unknown instruction '{name}'"

	info = instruction[name]

	#I-type need 3 operands: rd, rs1, imm
	if len(operands) != 3:
		return f"Errror: '{name}' needs 3 operands "

	try:

		rd = registers[operands[0]]

		#here use rd, offset(rs1)
		if name in ["lw", "jalr"]:
			imm_val = int(operands[1])
			rs1 = registers[operands[2]]

		#for addi, sltiu, etc use rd,rs1,imm
		else:
			rs1 = registers[operands[1]]
			imm_val = int(operands[2])

		
		#checking for immediate range 
		if 2047 < imm < -2048:
			return "Error: immediate out of range"

		imm = to_bin(imm_val,12)

		binarycode = imm + rs1 + info["f3"] + rd + info["opcode"]

		return binarycode

	except ValueError:
		return "Error: invalid immediate value"
	except KeyError:
		return "Error: invalid register"

#test

if __name__ == "__main__":

	print("Error Tests")





















