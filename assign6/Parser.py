#Parser module
class Parser:
	#the actual file handle
	file = None
	#array that holds the instructions
	instructions = []
	#stuff to keep track of current instruction
	currentInstructionIndex = 0
	currentInstruction = None
	
	#init that converts file to array
	def __init__(self, file):
		self.file = file
		#loop over file
		for line in self.file:
			#get ride of spaces
			line = line.replace(" ", "")
			#get rid of newlines
			line = line.replace("\n", "")
			line = line.replace("\r", "")
			#ignore comments
			line = line.split('/')[0]

			if line:
				self.instructions.append(line)
				
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
	
	#start the parser over and begin with 1st instruction again
	def reset(self):
		self.currentInstructionIndex = 0
		
		if len(self.instructions) != 0:
			self.currentInstruction = self.instructions[self.currentInstructionIndex]


	#return what kind of command we are on
	def commandType(self):
		if self.currentInstruction.startswith("@"):
			return "A_COMMAND"
		elif self.currentInstruction.startswith("("):
			return "L_COMMAND"
		else: 
			return "C_COMMAND"
	
	#get the symbol from @xxx or (xxx) 
	def symbol(self):
		if self.currentInstruction.startswith("@"):
			return self.currentInstruction.split("@")[1]
		elif self.currentInstruction.startswith("("):
			return self.currentInstruction.split("(")[1][:-1]
		else:
			return None
		
	#get the dest part of dest=comp;jump
	def dest(self):
		if "=" in self.currentInstruction:
			return self.currentInstruction.split("=")[0]
		else:
			return None
	
	#get the comp part of dest=comp;jump
	def comp(self):
		if "=" in self.currentInstruction:
			return self.currentInstruction.split("=")[1]
		else:
			return self.currentInstruction.split(";")[0]
	
	#get the jump part of dest=comp;jump
	def jump(self):
		if ";" in self.currentInstruction:
			return self.currentInstruction.split(";")[1]
		else:
			return None