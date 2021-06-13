import sys
from Parser import Parser
from AssemblyWriter import AssemblyWriter
import os

class VMTranslator():
    
    def __init__(self):
      self.path = sys.argv[1]
      self.outPutFilePath = self.path.split('.')[0] + '.asm'
      if os.path.isdir(self.path):
        self.outPutFilePath = self.path + '/' + self.path + '.asm'
      
      self.Main()
    
    def Main(self):
      if os.path.isdir(self.path):
        # Write Bootstrap code 
        asmFile = AssemblyWriter(self.outPutFilePath) 
        asmFile.writeInit()
        for filename in os.listdir(self.path):
          if filename.endswith(".vm"):
            asmFile = AssemblyWriter(self.outPutFilePath, filename[:-3]) 
            filePath = os.path.join(self.path, filename)
            commands = Parser(filePath).getCommands()
            self.writeAsmFile(commands, asmFile)
        asmFile.close()


      else:
        commands = Parser(self.path).getCommands()
        asmFile = AssemblyWriter(self.outPutFilePath, self.path.split('.')[0]) 
        self.writeAsmFile(commands, asmFile)
        asmFile.close()
        
    def writeAsmFile(self,  commands, asmFile):
      for commandObject in commands:
          
          if commandObject['type'] == 'C_ARITHMETIC':
            asmFile.writeArithmetic(commandObject['command'])
          
          if commandObject['type'] == 'C_BRANCH':
            asmFile.writeBranches(commandObject['command'], commandObject['arg1'])
          
          if commandObject['type'] in ['C_POP', 'C_PUSH']:
            asmFile.writePushPop(commandObject['type'], commandObject['arg1'], commandObject['arg2'])
          
          if commandObject['type'] == 'C_FUNCTION':
            asmFile.writeFunction(commandObject['arg1'], commandObject['arg2'])
          
          if commandObject['type'] == 'C_CALL':
            asmFile.writeCall(commandObject['arg1'], commandObject['arg2'])
          
          if commandObject['type'] == 'C_RETURN':
            asmFile.writeReturn()
      
    
VMTranslator()
