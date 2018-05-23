enum system_state {BASIC, CMD_WAITING, STATE_RESET=0xFF};
uint8_t system_state=BASIC;

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
 0b10000000
};

struct fifo256 {
 uint8_t fifo256::availr();
 uint8_t fifo256::availw();
 void fifo256::write(uint8_t);
 uint8_t fifo256::read();
 
 uint8_t fifo256::_read_head;
 uint8_t fifo256::_write_head;
 uint8_t fifo256::_data[256];
};

fifo256 incoming;
fifo256 cmd;

uint8_t drain_hw(uint8_t, fifo256 buf=incoming);
uint8_t drainctr=0x01;
uint8_t cmd_read_2=0;
void process_byte(uint8_t);
void queueCMD(uint8_t);
void setPins(uint8_t);

bool should_reset();
void(* RESET)(void) = 0; // stolen from Instructables lol but seems legit

// the setup routine runs once when you press reset:
void setup(){ 
	Serial.begin(9600);
	pinMode(RED_LED, OUTPUT);
	pinMode(YELLOW_LED, OUTPUT);
	pinMode(GREEN_LED, OUTPUT);
	pinMode(BLUE_LED, OUTPUT);
//	pinMode(CLEAR_LED, OUTPUT);
	pinMode(WHITE_LED, OUTPUT);
	
	// P.O.S.T.
	drainctr=0x01;
	do {
		// Iterates from 0x01 to 0xFF, inclusive,
		// then finishes with 0x00
		Serial.print(drainctr, HEX);
		process_byte(drainctr);
		Serial.println("");
	} while (drainctr++);
}

// the loop routine runs over and over again forever:
void loop(){
	if (system_state==BASIC){
		//1. Pop the FIFO into the LEDs
		//   (Waiting for a byte from HW if needed)
		while (!Serial.available())
			delay(100);
		incoming.write(Serial.read());
		
		process_byte(incoming.read());
		
		//2. FULLY DRAIN (our) fifo into the LEDs
		while (incoming.availr())
			process_byte(incoming.read());
	
		//3. Drain up to 16 bytes from the HW buffer
		drain_hw(16);
	}
}

void process_byte(uint8_t byte){
	if (byte & BITMASK_1BIT[7]){
		//High bit is SET/1
		return queueCMD(byte);
	} else {
		//High bit is UNSET/0
		return setPins(byte);
	}
}

void setPins(uint8_t pinStateByte){
	// http://forum.arduino.cc/index.php?topic=111711.msg839464#msg839464
	// digitalWrite presumes its second argument as bool-castable
	digitalWrite(WHITE_LED, pinStateByte & BITMASK_1BIT[0] );
	digitalWrite(RED_LED  , pinStateByte & BITMASK_1BIT[3] );
	digitalWrite(YELLOW_LED,pinStateByte & BITMASK_1BIT[2] );
	digitalWrite(GREEN_LED, pinStateByte & BITMASK_1BIT[1] );
	digitalWrite(BLUE_LED,  pinStateByte & BITMASK_1BIT[4] );
	
	// Delay ~1/32 of a second for digitalWrite()s to propagate
	delay(31);
	//TODO: don't use delay()
	// This will probably require a program rewrite however
}

void queueCMD(uint8_t byte){
	if (cmd.availw())
		cmd.write(byte);
}

uint8_t drain_hw(uint8_t qty=0, fifo256 buf){
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
	 buf.availw()
	){
		buf.write(Serial.read());
		drainctr++;
	}
	
	return drainctr;
}

uint8_t fifo256::availr(){
	return this->_write_head - this->_read_head;
}

uint8_t fifo256::availw(){
	return this->_read_head - this->_write_head;
}

uint8_t fifo256::read(){
	return this->_data[++this->_read_head];
}

void fifo256::write(uint8_t byte){
	this->_data[++this->_write_head]=byte;
}

bool should_reset(){
	cmd_read_2=0;
	do {	//STRCMP is for WUSSES
		if (cmd._data[cmd_read_2] == 0x52) // "R"
		if (cmd._data[cmd_read_2] == 0x53) // "S"
		if (cmd._data[cmd_read_2] == 0x0a) // "\n"
		return true;
	} while (++cmd_read_2);
	return false;
}
