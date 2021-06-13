## Virtual Machine ( Stack Arithmetic )
The first layer of abstraction above hardware is the Virtual Machine, it's essentialy like [the Virtual Machine of Java](https://en.wikipedia.org/wiki/Java_virtual_machine), the VM abstractions decomposes the RAM into a stack and several segments: local, argument, static, this, that.   

The VM comes with two commands that operate on those segments:     
**push**: pushes a value from the specified segment into the stack   
**pop**: pops a value from the stack into the specified segment   
and also several arithmetic and logical commands like: add, sub, and, or...   

The project is to develop a VM translator that translates VM code into Hack assembly code, this abstraction makes it easy to develop the compiler for the high level language (Jack) that will come later.   

## Project
The project is composed of 3 modules:  
1- **Parser**: parses the VM code into it's composite tokens   
2- **AssemblyWriter**: reads the parser output and produce hte coresponded assembly code   
3- **VMtranslator**: The main module that assemble the previous module, it takes the VM files ( or folder of VM files) as an input and generates the corresponding asm files  

