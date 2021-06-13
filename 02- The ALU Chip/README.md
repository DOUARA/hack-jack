## Binary Numbers System 
A numbers system is a way of representing numbers with symbols. 
**A positional numbers system** is a numbers system where the value of symbols depends on its position. 
The number of symbols (that we call digits) is called **the base**. 
In decimal system we have 10 digits: 0-9, in binary system we only got 2: 0 and 1. 

We do addition operation in binary numbers the same way we did addition for decimal numbers in school, more details for this can be found [here](http://web.math.princeton.edu/math_alive/Crypto/Lab1/BinAdd.html)

### Negative Numbers 
Negative numbers are represented with the [2's complement system](https://en.wikipedia.org/wiki/Two%27s_complement#:~:text=Two's%20complement%20is%20a%20mathematical,method%20of%20signed%20number%20representation.&text=Two's%20complement%20is%20the%20most,generally%2C%20fixed%20point%20binary%20values.) 
We can represent 2 powers n numbers for n number of bits, if we have a positive number x, -x = power(2, n) - x 

- What's nice about this representation is that we get additional operation for free, it means that we still can do the addition operation the same way and get the right results also for negative numbers, note that the overflowed bit should be ignored. ( This can be proved mathematically ).


## Project 
The goal of this project is to build the ALU chip ( Arithmetic Logic Unit ), which is the fundamental block in the CPU ( Central Processing Unit ), the ALU Chip implements multiple logical and Arithmetic operations including but not limited to:  AND, OR, NEG, NOT, addition, substraction... 

