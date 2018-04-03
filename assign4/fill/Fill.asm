// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
	//since the screen is 256*512, create a variable that is 8192
	@8192
	D = A
	@registersToFill
	M = D
	
	//load the keyboard variable
	@KBD
	D = M
	
	//if not pressed (0) go to white fill part
	@WHITEFILL
	D; JEQ
	
	//if pressed go to black fill part
	@BLACKFILL
	0; JMP
	
(WHITEFILL)
	//get registersToFill
	@registersToFill
	D = M
	
	//if registersToFill is < 0, go back to start
	@LOOP
	D; JLT
	
	//get registersToFill again
	@registersToFill
	D = M
	
	//get screen and add registersToFill to get register we need to fill
	@SCREEN
	A = D + A
	
	//fill the register with white
	M = 0
	
	//load and decrement registersToFill
	@registersToFill
	M = M - 1
	
	//go back to white fill start
	@WHITEFILL
	0; JMP
	
(BLACKFILL)
	//get registersToFill
	@registersToFill
	D = M
	
	//if registersToFill is < 0, go back to start
	@LOOP
	D; JLT
	
	//get registersToFill again
	@registersToFill
	D = M
	
	//get screen and add registersToFill to get register we need to fill
	@SCREEN
	A = D + A
	
	//fill the register with black
	//this is set to -1 which sets the 16 bit register to all 1s
	//There are 256 rows on the screen, and each row is split into 32 
	//consecutive 16 bit words, meaning we need to fill a 16 bit word of all
	//1s 256 * 32 or 8192 times
	M = -1
	
	//load and decrement registersToFill
	@registersToFill
	M = M - 1
	
	//go back to white fill start
	@BLACKFILL
	0; JMP
	
	