#NOTE: This class does not error check because of the use of maps. If a command that shouldnt be run comes in, this will crash when it tries to pull from the maps
#this is good enough for me
class CodeWriter:
	outputPath = ""
	outputFile = None
	#keeps track of how many logical comparisons we've made to create unique labels
	logicCounter = 0
	filename = ""
	#helpers
	#puts the head of the stack in the D register and decrements stack pointer
	load_stack_head_to_D = "@SP\nAM=M-1\nD=M\n"
	#pushes the current value of the D register to the stack and increments statck pointer
	push_d_to_stack = "@SP\nM=M+1\nA=M-1\nM=D\n"
	#map between the arithmetic operations and the boolean/arithmetic operations that are used on their corresponding registers
	arithmeticMap = {
		"add": "+",
		"sub": "-",
		"neg": "-",
		"eq":  "-",
		"lt": "-",
		"gt": "-",
		"and": "&",
		"or": "|",
		"not": "!"
	}
	#maps the logical stack operators to their jump directives in assembly
	logicalMap = {
		"eq": "JEQ",
		"lt": "JLT",
		"gt": "JGT"
	}
	#maps the memory access stack commands to their assembly keywords
	memoryMap = {
		"local": "LCL",
		"argument": "ARG",
		"this": "THIS",
		"that": "THAT",
		"pointer": "3",
		"temp": "5",
	}
	
	#takes in a file path and creates an output file to write to
	def __init__(self, path):
		self.outputPath = path
		#clears file in case this a redo
		self.outputFile = open(self.outputPath, 'w')
		self.outputFile.close()
		#appends to empty file
		self.outputFile = open(self.outputPath, 'a')
		
	#sets the filename for static memory stuff
	def setFileName(self, name):
		self.filename = name
	
	#writes the assembly for all the arithmetic commands
	def writeArithmetic(self, command):
		output = ""
		#get which operator should be used on x/y
		operator = self.arithmeticMap[command]
		
		#operations that use x and y
		if command in ["add", "sub", "eq", "gt", "lt", "and", "or"]:
			#store y in R13
			output += self.load_stack_head_to_D
			output += "@R13\nM=D\n" 
			
			#store X in R14 
			output += self.load_stack_head_to_D
			output += "@R14\nM=D\n"
			
			#perform the correct operation on R13 and R14 and store the result in D
			output += "@R14\nD=M\n@R13\nM=D" + operator + "M\n@R13\nD=M\n"
			
		#operations that only use y
		elif command in ["neg", "not"]:
			#store get Y from stack and store the result of the correct operation in D
			output += self.load_stack_head_to_D
			output += "D=" + operator + "D\n"
			
		#logical stuff needs more commands for branching
		if command in ["eq", "gt", "lt"]:
			#get what logical jump directive we need
			logical = self.logicalMap[command]
			
			#create a tag for where to go if this comp is true
			output += "@True" + str(self.logicCounter) + "\n"
			
			#jump with correct directive
			output += "D;" + logical + "\n"
			
			#if we dont jump, set D to false and jump to the part that sets the stack
			output += "@0\nD=A\n"
			output += "@Continue" + str(self.logicCounter) + "\n"
			output += "0;JMP\n"
			
			#if true, set D to 0
			output += "(True" + str(self.logicCounter) + ")\n@0\nD=!A\n"
			
			#this part is run no matter what (this tag holds the push T/F to stack, which is captured down there)
			output += "(Continue" + str(self.logicCounter) + ")\n"
			
			#increment logicCounter
			self.logicCounter += 1	
		
		#always dump d to stack at the end (this is the down there part)
		output += self.push_d_to_stack
		
		#write to file	
		self.outputFile.write(output)
		
	def writePushPop(self, command, segment, index):
		output = ""
		#push command
		if command == "C_PUSH":
			#constant
			if segment == "constant":
				#load the constant and store in D
				output += "@" + index + "\nD=A\n"
				output += self.push_d_to_stack
				
			#static - uses the filname.index convention described in the book
			elif segment == "static":
				#get the @xxx.index label and does D=M
				output += "@" + self.filename.split(".")[0] + "." + str(index) + "\n"
				output += "D=M\n"
				output += self.push_d_to_stack
				
			#everything else
			else:
				#get the assembly tag for the segment we are trying to address
				memTag = self.memoryMap[segment]
				
				#get the segment and store in D
				output += "@" + memTag + "\n"
				
				#if we want pointer or temp, we store the A register in D, since pointer and temp refer to constants 3 and 5
				if segment in ["pointer", "temp"]:
					output += "D=A\n"
				#if we have anything else, we store the M register in D, since all other segments are stored in the memory of their @tag
				else:
					output += "D=M\n"
				
				#get the constant for index and add to D, storing in A register (essentially doing the pointer math we need)
				output += "@" + str(index) + "\n"
				output += "A=D+A\n"
				
				#set D to Memory[A](the memory location of the index of the segment we want to access)
				output += "D=M\n"
				
				#push d to the stack to move the memory onto the stack
				output += self.push_d_to_stack
		#pop command
		elif command == "C_POP":
			#get the correct @tag
			#static needs the filename.index convention
			if segment == "static":
				memTag = self.filename.split(".")[0] + "." + str(index)
			else:
				#everything else just uses the assembly reserved words
				memTag = self.memoryMap[segment]
				
			#get the value of the segment tag and store in D
			output += "@" + memTag + "\n"
			
			#if we have pointer, temp, or static, set D to A since we want the constant from the @ tag
			if segment in ["pointer", "temp", "static"]:
					output += "D=A\n"
			else:
				#everything else set D to M since we want the memory location stored in the segment tag
				output += "D=M\n"
			
			#only do the pointer math if we aren't using segment
			if segment != "static":
				#get the constant for index and add to D, storing in D regiter
				output += "@" + str(index) + "\n"
				output += "D=D+A\n"
			
			#store D (address we want to pop to) for later
			output += "@R13\n"
			output += "M=D\n"
			
			#set D to stack head, get r13 memory value (the address we want to pop to) and store it in A
			#when we do the final M=D, we set Memory[address we want to pop to] = D (the value from the top of the stack)
			output += self.load_stack_head_to_D
			output += "@R13\nA=M\nM=D\n"
		
		#write the assembly to the output file
		self.outputFile.write(output)
		
	#closes output file
	def close(self):
		self.outputFile.close()
		
	