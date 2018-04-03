import sys
import os
from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

#converts decimal to binary and pads to 16 digits
def decimalToBinary(dec): 

	if isInt(dec):
		#get binary
		temp = bin(int(dec)).split("b")[1]
		
		#pad/error check
		if len(temp) > 16:
			return None
		else:
			return temp.rjust(16, '0')
	else:
		return None
	
#function to check if a string is an integer	
def isInt(n):
	try:
		int(n)
		return True
	except ValueError:
		return False
	
def main():
	#make sure they used the program right
	if len(sys.argv) != 2:
		print("usage: python assempler.py <some .asm file>")
		return
	
	#get the path to the asm file
	path = sys.argv[1]
	
	#make sure it is an asm file
	if path.split('.')[1] != 'asm':
		print("Error: you did not supply an asm file")
		
	#parse the asm file to get the instructions in a good format to parse
	instructions = []
	file = open(path, 'r');
	
	#create modules and keep track of current ram address for symbols
	parser = Parser(file)
	code = Code()
	symbolTable = SymbolTable()
	symbolEntry = 16
	
	#holds the binary output lines
	output =  []
	
	#first pass to add L command labels to symbol table
	rom = 0
	while parser.hasMoreCommands():
		if parser.commandType() == "L_COMMAND":
			print(parser.symbol())
			symbolTable.addEntry(parser.symbol(), rom)
		else:
			rom += 1
		
		parser.advance()
		
	#reset the parser for 2nd pass
	parser.reset()
	
	#2nd pass
	while parser.hasMoreCommands():
		#get command type and create a command to output
		iType = parser.commandType()
		command = None
		print(parser.currentInstruction)
		if iType == 'C_COMMAND':
			#get all parts of c command in binary
			dest = code.dest(parser.dest())
			comp = code.comp(parser.comp())
			jump = code.jump(parser.jump())
			
			#error check
			if dest is None or comp is None or jump is None:
				print("Error: invalid dest, comp, or jump")
				return
			else:
				command = '111' + comp + dest + jump
		elif iType == 'A_COMMAND':
			#get symbol and error check
			symbol = parser.symbol()
			if symbol is None:
				print("Error: invalid symbol declaration")
				return
				
			#just convert to binary if integer
			if isInt(symbol):
				command = decimalToBinary(symbol)
			else:
				#if the symbol isnt in the symbol table add it
				if not symbolTable.contains(symbol):
					symbolTable.addEntry(symbol, symbolEntry)
					symbolEntry += 1
				#convert address from symbol table to binary
				command = decimalToBinary(symbolTable.getAddress(symbol))
		#since l commands are already handles, dont do anything
		elif iType == 'L_COMMAND':
			parser.advance()
			continue
				
		#error check command and add to output
		if command is None:
			print("Error: binary string longer than 16bits")
			return
		else:
			output.append(command)
			
		#next line
		parser.advance()
	
	#write to file but change to .hack
	outputPath = os.path.splitext(path)[0] + '.hack'
	outfile = open(outputPath, 'w')
	
	for binary in output:
		outfile.write(binary + '\n')
						
if __name__ == '__main__':
	main()
	