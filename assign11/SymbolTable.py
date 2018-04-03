import sys


class SymbolTableEntry(object):
    """An entry in the symbol table that holds the variable type, what kind it is
    (STATIC, FILED, ARG, or VAR) and its index in the symbol table"""
    nameMap = {
        "static": "static",
        "field": "this",
        "arg": "argument",
        "var": "local"
    }
    def __init__(self, varType, kind, index):
        super(SymbolTableEntry, self).__init__()
        self.varType = varType
        self.kind = self.nameMap[kind]
        self.index = index


class SymbolTable(object):
    """A symbol table for mapping identifiers to variables for compilation"""

    def __init__(self):
        super(SymbolTable, self).__init__()
        self.classTable = {}
        self.subTable = {}
        self.staticIndex = 0
        self.fieldIndex = 0
        self.argIndex = 0
        self.varIndex = 0

    def startSubroutine(self):
        """Clears the subTable and wipes the subroutine scope counters"""
        self.subTable = {}
        self.argIndex = 0
        self.varIndex = 0

    def define(self, name, varType, kind):
        """Creates a new symbol table entry and assigns it the correct index"""
        if kind == "static":
            self.classTable[name] = SymbolTableEntry(varType, kind, self.staticIndex)
            self.staticIndex += 1
        elif kind == "field":
            self.classTable[name] = SymbolTableEntry(varType, kind, self.fieldIndex)
            self.fieldIndex += 1
        elif kind == "arg":
            self.subTable[name] = SymbolTableEntry(varType, kind, self.argIndex)
            self.argIndex += 1
        elif kind == "var":
            self.subTable[name] = SymbolTableEntry(varType, kind, self.varIndex)
            self.varIndex += 1
        else:
            print("Error: invalid kind for SymbolTable")
            sys.exit(1)

    def varCount(self, kind):
        """Returns how many variables of kind k have been defined so far"""
        if kind == "static":
            return self.staticIndex
        elif kind == "field":
            return self.fieldIndex
        elif kind == "arg":
            return self.argIndex
        elif kind == "var":
            return self.varIndex
        else:
            print("Error: invalid kind for varCount")
            sys.exit(1)

    def kindOf(self, name):
        """Returns the kind of the table entry with name name"""
        if name in self.classTable:
            return self.classTable[name].kind
        elif name in self.subTable:
            return self.subTable[name].kind
        else:
            return None

    def typeOf(self, name):
        """Returns the varType of the table entry with name name"""
        if name in self.classTable:
            return self.classTable[name].varType
        elif name in self.subTable:
            return self.subTable[name].varType
        else:
            return None

    def indexOf(self, name):
        """Returns the index of the table entry with name name"""
        if name in self.classTable:
            return self.classTable[name].index
        elif name in self.subTable:
            return self.subTable[name].index
        else:
            return None
