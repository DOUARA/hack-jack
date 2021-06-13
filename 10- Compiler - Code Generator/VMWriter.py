
class VMWriter:
    def __init__(self, outPutFilePath):
        self.outputFile = open(outPutFilePath, "w")

    def writePush(self, segment, index):
        #print(segment, index)
        self.outputFile.write('push ' + segment + ' ' + str(index) + '\n')

    def writePop(self, segment, index):
        self.outputFile.write('pop ' + segment + ' ' + str(index) + '\n')

    def writeArithmetic(self, symbol):
        op = ''
        operationsMapping = {
                '+' : 'add',
                '-' : 'sub',
                '*' : 'call Math.multiply 2',
                '/' : 'call Math.divide 2',
                '&' : 'and',
                '|' : 'or',
                '<' : 'lt',
                '>' : 'gt',
                '=' : 'eq'
        }
        if symbol in operationsMapping:
            op = operationsMapping[symbol]
            self.outputFile.write(op + '\n')
            return
        return 'Error: Undefined Arithmetic Operation'

    def writeCommand(self, command):
        self.outputFile.write(command + '\n')
    
    def writeLabel(self, label):
        self.outputFile.write('label ' + label + '\n')

    def writeGoto(self, label):
        self.outputFile.write('goto ' + label + '\n')
    
    def writeIf(self, label):
        self.outputFile.write('if-goto ' + label + '\n')

    def writeCall(self, name, nArgs):
        self.outputFile.write('call ' + name + ' ' + str(nArgs) + '\n')

    def writeFunction(self, name, nLocals):
        self.outputFile.write('function ' + name + ' ' + str(nLocals) + '\n')
    
    def writeReturn(self):
        self.outputFile.write('return \n')
    
    def close(self):
        self.outputFile.close()
    
    
    

    
