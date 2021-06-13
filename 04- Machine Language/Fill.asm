// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.



(LOOP)
@i
M = 0

@KBD
D = M

@PRINT
D;JGT

@CLEAR
D;JEQ

@LOOP
0;JMP

(PRINT)
@SCREEN 
D = A
@i
D = D + M
@KBD
D=D-A
@PRINTPIXEL
D;JLT

@LOOP
0;JMP

(PRINTPIXEL)
@i
D = M
M = M + 1

@SCREEN
D = D + A
A = D
M = -1

@PRINT
0;JMP


(CLEAR)
@SCREEN 
D = A
@i
D = D + M
@KBD
D=D-A
@CLEARPIXEL
D;JLT

@LOOP
0;JMP

(CLEARPIXEL)
@i
D = M
M = M + 1

@SCREEN
D = D + A
A = D
M = 0

@CLEAR
0;JMP











