const uint8_t WHITE_LED = A5;
const uint8_t CLEAR_LED = A4;
const uint8_t BLUE_LED = A3;
const uint8_t GREEN_LED = A2;
const uint8_t YELLOW_LED = A1;
const uint8_t RED_LED = A0;
const uint8_t BITMASK_1BIT[] = {
 0b00000001,
 0b00000010,
 0b00000100,
 0b00001000,
 0b00010000,
 0b00100000,
 0b01000000,
 0b10000000,
};

uint8_t incomingFifo[256];
uint8_t fifoWriteIndex=0;
uint8_t fifoReadIndex=0;

uint8_t drainctr;
uint8_t drain_hw(uint8_t);
uint8_t fifo_avail();
uint8_t fifo_pop_safe();
void pin_batch(uint8_t);

// the setup routine runs once when you press reset:
void setup(){ 
	Serial.begin(9600);
	pinMode(RED_LED, OUTPUT);
	pinMode(YELLOW_LED, OUTPUT);
	pinMode(GREEN_LED, OUTPUT);
//	pinMode(BLUE_LED, OUTPUT);
//	pinMode(CLEAR_LED, OUTPUT);
	pinMode(WHITE_LED, OUTPUT);
	
	// P.O.S.T.
	drainctr=0x01;
	do {
		// Iterates from 1 to 255, inclusive,
		// then 0
		Serial.print(drainctr, HEX);
		pin_batch(drainctr);
		Serial.println("");
	} while (drainctr++);
}

void pin_batch(uint8_t state){
	// This is ONLY MEANT TO BE USED
	// IF THE HIGH BIT IS NOT SET
	if (state & BITMASK_1BIT[7])
		return;
	// for now, just exit inertly if
	// passed a byte with high-bit=1

	// http://forum.arduino.cc/index.php?topic=111711.msg839464#msg839464
	// digitalWrite presumes its second argument as bool-castable
	digitalWrite(WHITE_LED, state & BITMASK_1BIT[0] );
	digitalWrite(RED_LED  , state & BITMASK_1BIT[3] );
	digitalWrite(YELLOW_LED,state & BITMASK_1BIT[2] );
	digitalWrite(GREEN_LED, state & BITMASK_1BIT[1] );
	
	// Delay ~1/32 of a second for digitalWrite()s to propagate
	delay(31);
	//TODO: don't use delay()
	// This will probably require a program rewrite however
}

// the loop routine runs over and over again forever:
void loop(){
	//1. Pop the FIFO into the LEDs
	//   (Waiting for a byte if needed)
	pin_batch(fifo_pop_safe());
	
	//2. FULLY DRAIN our fifo into the LEDs
	while (fifo_avail())
		pin_batch(fifo_pop_safe());

	//3. Drain up to 16 bytes from the HW buffer
	drain_hw(16);
}
//	(4. repeat steps 1-3)

uint8_t drain_hw(uint8_t qty){
	// As long as ALL OF:
	//  a) We have unfilled (or unlimited) drain request
	//  b) There is stuff available to fill it
	//  c) We haven't filled our buffer
	// keep popping data from the HW FIFO
	
	drainctr=0;
	
	while (
	 ( (qty==0) || (drainctr < qty) )
	&&
	 Serial.available()
	&&
	 fifoWriteIndex+1 != fifoReadIndex
	){
		incomingFifo[++fifoWriteIndex] = Serial.read();
		drainctr++;
	}
	
	return drainctr;
}

uint8_t fifo_avail(){
	return fifoWriteIndex - fifoReadIndex;
}

uint8_t fifo_pop_raw(){
	return incomingFifo[++fifoReadIndex];
}

uint8_t fifo_pop_safe(){
	if (fifo_avail())
		return fifo_pop_raw();
	else
		while (not drain_hw(1))
		 delay(100);
	// This code SHOULD NOT execute until drain_hw returns True
	return fifo_pop_raw();
}
