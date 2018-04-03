import sys
import os
from Parser import Parser
from CodeWriter import CodeWriter
	
def main():
	#make sure they used the program right
	if len(sys.argv) != 2:
		print("usage: python VMtranslator.py <some .vm file or a directory with .vm files in it>")
		return
	
	#holds the open file descriptors to pass to the Parser constructor
	fileHandles = []
	inputPath = sys.argv[1]
	outputPath = ""
	#see if file or directory
	if inputPath.endswith(".vm"):
		#file
		vmFile = open(inputPath, 'r')
		fileHandles.append(vmFile)
		#set output path to be the vm file but with .asm extension
		outputPath = inputPath.replace(".vm", ".asm")
		
	elif os.path.isdir(inputPath):
		#make sure that the path doesn't end in a slash for a directory
		if inputPath.endswith("/"):
			inputPath = inputPath[:-1]
		#get .vm files and open them from directory
		for file in os.listdir(inputPath):
			if file.endswith(".vm"):
				vm = open(os.path.join(inputPath, file), 'r')
				fileHandles.append(vm)
		#outputpath is the path/directoryName.asm
		outputPath = inputPath + "/" + os.path.basename(inputPath) + ".asm"
	else:
		#error
		print("You must enter a single .vm file or a directory with .vm files in it")
	
	#instantiate the codewriter with the correct output path
	writer = CodeWriter(outputPath)
	#run through all the .vm files we have
	for file in fileHandles:
		#make a new parser for each .vm file
		parser = Parser(file)
		#make sure to give the writer the current file name for static memory access stuff
		writer.setFileName(os.path.basename(file.name))
		#write either arithmetic or memory access commands
		while (parser.hasMoreCommands()):
			if parser.commandType() == "C_ARITHMETIC":
				writer.writeArithmetic(parser.arg1())
			elif parser.commandType() == "C_PUSH" or parser.commandType() == "C_POP":
				writer.writePushPop(parser.commandType(), parser.arg1(), parser.arg2())
				
			parser.advance()
	#close the output file
	writer.close()
if __name__ == '__main__':
	main()
	