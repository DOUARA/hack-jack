## Boolean Algebra 
Named according to his inventor [George Boole](https://en.wikipedia.org/wiki/George_Boole), Boolean Algebra is the field of study of boolean values (aka binary values), those values can be represented in many forms like (True, false), (Yes, No), (0,1). 
We can perform certain actions on boolean values to produce other boolean values, those actions are called **boolean functions** 

### Boolean functions 
A boolean function is a function that takes a boolean value as an input and return a boolean value as a result of some kind of logical opeartions, the very basic functions are called **operators** which are: AND, OR, NOT.

The boolean function can be specified with a **truth table** or an **expresion**, the expression deducted from the truth-table is called **Canonical Expression**

Boolean Functions Examples: 
```
And(x,y)
Or(x,y)
Not(x,y) 
Nand(x,y) = Not(And(x,y))
Nor(x,y) = Not(Or(x,y))
```
It turns out that all basic operators can be constructed fron **Nand** function only 
This result has far-reaching practical implications, once we have in our disposal a physical device that implements **Nand** we can use many copies of this device ( wired in some way ) to implement in hardware any boolean function 


## Logic Gates 
Also called logic chips, A logic gate is a physical device that implements a boolean function, electric ones are the most common, and the boolean values are represented with high/low voltages, they are implemented with a tiny switches called **Transistors**

We use HDL (Hardware Description Language) also know as VHDL to specify the gate topology and also for testing purposes, it's a step that preceeds the chip production, the very common and commercial HDLs are VHDL and verilog. 

in this project and in the ones that come after we will use a basic HDL designed by the course creators. 

## Project 
Gates built on this project:
- And
- And16
- DMux
- DMux4Way
- DMux8Way
- Mux 
- Mux4Way16
- Mux8Way16
- Mux16
- Not 
- Not16
- Or
- Or8way
- Or16
- Xor
