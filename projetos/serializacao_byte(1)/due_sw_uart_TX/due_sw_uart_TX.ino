#include "sw_uart.h"

due_sw_uart uart;

void setup() {
  //Serial.begin(115200);
  //due_sw_uart *uart, rx, tx, stopbits, databits, paritybit
  sw_uart_setup(&uart, 4, 3, 1, 8, SW_UART_EVEN_PARITY);
}

void loop() {
 test_write();
}

void test_write() {
  sw_uart_write_string(&uart,"a");
  delay(1000);
}
