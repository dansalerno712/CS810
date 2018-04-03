class SymbolTable:
	#dictionary to hold symbol table
	table = None
	
	#fill symbol table with os predefined symbols
	def __init__(self):
		self.table = {
			"SP": 0,
			"LCL": 1,
			"ARG": 2,
			"THIS": 3,
			"THAT": 4,
			"R0": 0,
			"R1": 1,
			"R2": 2,
			"R3": 3,
			"R4": 4,
			"R5": 5,
			"R6": 6,
			"R7": 7,
			"R8": 8,
			"R9": 9,
			"R10": 10,
			"R11": 11,
			"R12": 12,
			"R13": 13,
			"R14": 14,
			"R15": 15,
			"SCREEN": 16384,
			"KBD": 24576
		}
		
	#add new symbol and address to table
	def addEntry(self, symbol, address):
		self.table[symbol] = address
		
	#check if a symbol is in the table
	def contains(self, symbol):
		return symbol in self.table
	
	#get the address of a symbol from the table
	def getAddress(self, symbol):
		if symbol in self.table:
			return self.table[symbol]
		else:
			return None