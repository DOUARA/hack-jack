import sys
import ntpath

class AssemblyWriter():
  def __init__(self, outputFile):
    self.fileName = ntpath.basename(outputFile).split('.')[0]
    self.file = open(outputFile, "w")
    self.iterator = 0
    self.asmCode = ''

  def close(self):
    if self.asmCode:
      endCode = '(END)\n'
      endCode += '@END\n' 
      endCode += '0;JMP'
      return self.file.write(endCode)  
    self.file.close()

  '''
  Writes the assembly code in the output file for branchings commands
    Parameters:
      command (str): the branching command 
      arg (str): the argument of the command 
     
    Returns:
      None
  '''
  def writeBranches(self, command, arg):
    asmCode  = '// Command: ' + command + ' ' + arg + '\n'
    lineBreak = '\n'
    if command == 'label':
      asmCode += '(' + arg + ')' + lineBreak

    if command == 'goto':
      asmCode += '@' + arg + lineBreak
      asmCode += '0;JMP' + lineBreak

    if command == 'if-goto':
      asmCode += '@SP' + lineBreak 
      asmCode += 'M=M-1' + lineBreak
      asmCode += 'A=M' + lineBreak
      asmCode += 'D=M' + lineBreak 
      asmCode += '@' + arg + lineBreak
      asmCode += 'D;JNE' + lineBreak
     

    self.iterator +=1
    self.asmCode += asmCode
    self.file.write(asmCode)
    

  '''
  Writes the assembly code in the output file for an arithmetic command
    Parameters:
      command (str): the arithmetic command 
     
    Returns:
      None
  '''
  def writeArithmetic(self, command):
    asmCode  = '// Command: ' + command + '\n'
    lineBreak = '\n'
    
    # add and sub mapping
    addSubMapping = {
      'add': '+',
      'sub': '-', 
      'and': '&',
      'or': '|'
    }

    if command in addSubMapping.keys():
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=M' + addSubMapping[command] + 'D' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak

    # Negation & not mapping
    negNotMapping = {
      'neg': '-',
      'not': '!'
    }
    if command in negNotMapping.keys():
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=' + negNotMapping[command] + 'D' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak

    # gt, lt, eq opeartions 
    compareMapping = {
      'gt': {
        'truthy': 'JGT',
        'falsy': 'JLE',
      },
      'lt': {
        'truthy': 'JLT',
        'falsy': 'JGE',
      },
      'eq': {
        'truthy': 'JEQ',
        'falsy': 'JNE',
      }
    }

    if command in compareMapping.keys():
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M-1' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'D=M-D' + lineBreak
      asmCode  += '@TRUE_'+ str(self.iterator) + lineBreak
      asmCode  += 'D;' + compareMapping[command]['truthy'] + lineBreak
      asmCode  += '@FALSE_'+ str(self.iterator) + lineBreak
      asmCode  += 'D;' + compareMapping[command]['falsy'] + lineBreak
      
      asmCode  += '(TRUE_'+ str(self.iterator) +')' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=-1' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak
      asmCode  += '@CONINUE_' + str(self.iterator) + lineBreak
      asmCode  += '0;JMP' + lineBreak

      asmCode  += '(FALSE_'+ str(self.iterator) +')' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'A=M' + lineBreak
      asmCode  += 'M=0' + lineBreak
      asmCode  += '@SP' + lineBreak
      asmCode  += 'M=M+1' + lineBreak
      asmCode  += '(CONINUE_' + str(self.iterator) + ')' + lineBreak
    self.iterator +=1
    self.asmCode += asmCode
    self.file.write(asmCode)
   
      
  '''
  Writes the  assembly code in the output file for for push or pop commands
    Parameters:
      commandType (str): the type of the command: C_POP or C_PUSH
      segmentName (str): the name of the segmant: temp, static. argument, ...
      index (str): the index in the command

    Returns:
      None
  '''
  def writePushPop(self, commandType, segment, index ):
      asmCode  = '// Command: ' + commandType + ' ' + segment + ' ' + index + '\n'
      lineBreak = '\n'

      # Segments Assembly Variables Mapping. 
      segmentsMapping = {
          'local': 'LCL',
          'argument': 'ARG',
          'this': 'THIS',
          'that': 'THAT',
          'temp': '5'
      }

      # PUSH command Code Generation
      if commandType == 'C_PUSH':
         
        # Segments: local, argument, this, that, temp
        if segment in segmentsMapping.keys():
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@' + segmentsMapping[segment] + lineBreak
          if segment == 'temp':
            asmCode += 'A=D+A' + lineBreak
          else:
            asmCode += 'A=D+M' + lineBreak
          asmCode += 'D=M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M+1' + lineBreak
         
        # Segment: constant
        if segment == 'constant':
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M+1' + lineBreak

        # Segment: static
        if segment == 'static':
          asmCode += '@' + self.fileName + '.' + index + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M+1' + lineBreak
        
        # Segment: pointer
        if segment == 'pointer' and (index == '0' or index == '1') :
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@THIS_B' + str(self.iterator) + lineBreak
          asmCode += 'D;JEQ'  + lineBreak
          asmCode += '@THAT_B'  + str(self.iterator) + lineBreak
          asmCode += 'D;JGT'  + lineBreak
          
          # THIS Branch
          asmCode += '(THIS_B' + str(self.iterator) + ')'  + lineBreak
          asmCode += '@THIS' + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M+1' + lineBreak
          asmCode  += '@CONINUE_' + str(self.iterator) + lineBreak
          asmCode  += '0;JMP' + lineBreak
         
          # THAT Branch
          asmCode += '(THAT_B' + str(self.iterator) + ')'  + lineBreak
          asmCode += '@THAT' + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M+1'  + lineBreak
          asmCode  += '(CONINUE_' + str(self.iterator) + ')' + lineBreak

      # POP command Code Generation
      if commandType == 'C_POP':
        
        # Segments: local, argument, this, that, temp
        if segment in segmentsMapping.keys():
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@' + segmentsMapping[segment] + lineBreak
          if segment == 'temp':
            asmCode += 'D=D+A' + lineBreak
          else:
            asmCode += 'D=D+M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M-1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'D=M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M+1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak

        # No pop command for constant segmant 

        # Segment: static
        if segment == 'static':
          asmCode += '@' + self.fileName + '.' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'M=M-1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'D=M' + lineBreak
          asmCode += '@SP' + lineBreak
          asmCode += 'A=M+1' + lineBreak
          asmCode += 'A=M' + lineBreak
          asmCode += 'M=D' + lineBreak

        # Segment: pointer
        if segment == 'pointer' and (index == '0' or index == '1') :
          asmCode += '@' + index + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@THIS_B' + str(self.iterator) + lineBreak
          asmCode += 'D;JEQ' + lineBreak
          asmCode += '@THAT_B' + str(self.iterator) + lineBreak
          asmCode += 'D;JGT' + lineBreak
          
          # THIS Branch
          asmCode += '(THIS_B' + str(self.iterator) + ')' + lineBreak
          asmCode += '@THIS'  + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M-1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M+1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode  += '@CONINUE_' + str(self.iterator) + lineBreak
          asmCode  += '0;JMP' + lineBreak

          # THAT Branch
          asmCode += '(THAT_B' + str(self.iterator) + ')' + lineBreak
          asmCode += '@THAT'  + lineBreak
          asmCode += 'D=A'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'M=M-1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'D=M'  + lineBreak
          asmCode += '@SP'  + lineBreak
          asmCode += 'A=M+1'  + lineBreak
          asmCode += 'A=M'  + lineBreak
          asmCode += 'M=D' + lineBreak
          asmCode  += '(CONINUE_' + str(self.iterator) + ')' + lineBreak

      self.iterator +=1
      self.asmCode += asmCode
      self.file.write(asmCode)
