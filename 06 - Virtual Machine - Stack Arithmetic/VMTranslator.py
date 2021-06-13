import sys
from Parser import Parser
from AssemblyWriter import AssemblyWriter

class VMTranslator():
    def __init__(self):
      self.Main()
    def Main(self):
      commands = Parser(sys.argv[1]).getCommands()
      outputFilePath = sys.argv[1].split('.')[0] + '.asm'
      asmFile = AssemblyWriter(outputFilePath)
      for commandObject in commands:
          if commandObject['type'] == 'C_ARITHMETIC':
            asmFile.writeArithmetic(commandObject['command'])
          if commandObject['type'] == 'C_BRANCH':
            asmFile.writeBranches(commandObject['command'], commandObject['arg1'])
          if commandObject['type'] in ['C_POP', 'C_PUSH']:
            asmFile.writePushPop(commandObject['type'], commandObject['arg1'], commandObject['arg2'])
      asmFile.close()
    
VMTranslator()
