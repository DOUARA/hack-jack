import sys
import pprint

class SymbolTable:
    
    def __init__(self):
        self.symbolTable =  {
                                'class': [],
                                'subroutine': []
                            }
        self.scope = ''

    def startSubroutine(self):
       self.symbolTable['subroutine'] = []

    def define(self, varName, varType, varKind):
        # Set the current scope
        if varKind in ['static', 'field']:
            self.scope = 'class'
        
        if varKind in ['argument', 'local']:
            self.scope = 'subroutine'
        
        varIndex = 0
        for elem in self.symbolTable[self.scope]:
            if elem['name'] == varName:
                sys.exit("ERROR: Variabe " + varName + ' have already been declared!')
            if elem['kind'] == varKind:
                varIndex += 1
       
        row = { 'name': varName, 'type': varType, 'kind': varKind, 'index': varIndex }
        
        self.symbolTable[self.scope].append(row)
        

    def kindOf(self, varName):
        for elem in self.symbolTable['subroutine'] + self.symbolTable['class']:
            if elem['name'] == varName:
                return elem['kind']
        
        return None

    def typeOf(self, varName):
        for elem in self.symbolTable['subroutine'] + self.symbolTable['class']:
            if elem['name'] == varName:
                return elem['type']
        return None

    def indexOf(self, varName):
        for elem in self.symbolTable['subroutine'] + self.symbolTable['class']:
            if elem['name'] == varName:
                return elem['index']
        return None

    def getFieldsCount(self):
        count = 0
        for var in self.symbolTable['class']:
            if var['kind'] == 'field':
                count += 1
        return count

    def getLocalsCount(self):
        count = 0
        for var in self.symbolTable['subroutine']:
            if var['kind'] == 'local':
                count += 1
        return count

    def getTable(self):
        pp = pprint.PrettyPrinter(indent=2)
        return pp.pprint(self.symbolTable)
        
        



    

