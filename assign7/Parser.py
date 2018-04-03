import sys

#Parser module
class Parser:
	#the actual file handle
	file = None
	#array that holds the instructions
	instructions = []
	#stuff to keep track of current instruction
	currentInstructionIndex = 0
	currentInstruction = None
	
	#array to lookup arithmetic instructions
	arithmeticInstructions = ["add", "sub", "neg", "eq", "gt", "lt",
							  "and", "or", "not"]
	
	#init that converts file to array
	def __init__(self, file):
		self.file = file
		#loop over file
		for line in self.file:
			#get ride of extra spaces
			line = " ".join(line.split())
			#get rid of newlines
			line = line.replace("\n", "")
			line = line.replace("\r", "")
			#ignore comments
			line = line.split('/')[0]

			if line:
				self.instructions.append(line)
				
		#set current instruction if there actual instructions to process
		if len(self.instructions) != 0:
			self.currentInstruction = self.instructions[self.currentInstructionIndex]
	
	#just check if current index is at the end of instruction array
	def hasMoreCommands(self):
		return self.currentInstructionIndex != len(self.instructions)
	
	#get the next instruction
	def advance(self):
		self.currentInstructionIndex += 1
		
		if self.hasMoreCommands():
			self.currentInstruction = self.instructions[self.currentInstructionIndex]

	#return what kind of command we are on
	def commandType(self):
		keyword = self.currentInstruction.split(" ")[0]
		if keyword in self.arithmeticInstructions:
			return "C_ARITHMETIC"
		elif keyword == "push":
			return "C_PUSH"
		elif keyword == "pop":
			return "C_POP"
		elif keyword == "label":
			return "C_LABEL"
		elif keyword == "goto":
			return "C_GOTO"
		elif keyword == "if":
			return "C_IF"
		elif keyword == "function":
			return "C_FUNCTION"
		elif keyword == "return":
			return "C_RETURN"
		elif keyword == "call":
			return "C_CALL"
		else:
			print("Error: invalid command type found")
			sys.exit()
	
	#get the 1st argument of a command, for arithmetic, return the add/sub/etc
	def arg1(self):
		if self.commandType() == "C_RETURN":
			print("Error: arg1() should not be called when current command is C_RETURN")
			sys.exit()
		elif self.commandType() == "C_ARITHMETIC":
			return self.currentInstruction
		else:
			return self.currentInstruction.split(" ")[1]
			
	#get the 2nd argument, only called if command is push, pop, function, or callable
	def arg2(self):
		if self.commandType() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
			return self.currentInstruction.split(" ")[2]
		else:
			print("Error: arg2 called with incorrect command type")
			sys.exit()