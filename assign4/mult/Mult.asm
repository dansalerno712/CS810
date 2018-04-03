//multiplies R0 and R1 and stores in R2 by adding R0 to R2 for R1 times
	//set register 2 to 0
	@2
	D = M
	M = 0
	
	//store the value of R1 in a variable i
	@1
	D = M
	@i
	M = D
(LOOP)
	//get the value in i
	@i
	D = M
	
	//if the value in i is 0, jump to end
	@END
	D; JEQ
	
	//load value in register 0
	@0
	D = M
	
	//load value in register 2 and add value from register 0
	@2
	M = D + M
	
	//load and decrement i
	@i
	M = M - 1
	
	//jump back to loop
	@LOOP
	0; JMP
	
(END)
	@END
	0; JMP
	
