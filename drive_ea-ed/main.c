#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/irq.h"
#include "hardware/timer.h"
#include "hardware/adc.h"
#include "hardware/uart.h"
#include "hardware/pwm.h"
#include "pico/multicore.h"
#include "hardware/clocks.h"

#define INPUT_PIN 21       // Pino GPIO para a entrada com interrupção
#define OUTPUT_PIN 20      // Pino GPIO para a saída
#define LED_PIN 25
uint8_t ID_DEVICE = 0x02;
uint16_t timer_recv_uart = 0;
bool habilita_recv_uart = true;
bool fim_de_comunicacao = false;

#define UART_ID uart0
#define BAUD_RATE 9600
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY UART_PARITY_NONE

#define UART_RE 3
#define UART_DE 2
#define RE_DE_SEND 1
#define RE_DE_RECV 0
#define RE_DE_HIGHZ 2

#define UART_TX_PIN 0
#define UART_RX_PIN 1

uint8_t command[12];
uint8_t cmd_crc[12];
uint8_t response[12];

void limpa_buffer(){
    //Limpa buffer de comando
        for ( int i=0;i<12;i++ ){
                command[i]=0;
        }
        for ( int i=0;i<12;i++ ){
                response[i]=0;
        }
        for ( int i=0;i<12;i++ ){
                cmd_crc[i]=0;
        }
}

void toggle_led(){
     gpio_put(LED_PIN, 1);
        sleep_ms(500);  // Aguardar 500 milissegundos (0,5 segundo)
        gpio_put(LED_PIN, 0);
        sleep_ms(500);  // Aguardar mais 500 milissegundos 
}

void toggle_led_fast(){
        gpio_put(LED_PIN, 1);
        sleep_ms(100);  // Aguardar 500 milissegundos (0,5 segundo)
        gpio_put(LED_PIN, 0);
        sleep_ms(100);  // Aguardar mais 500 milissegundos 
}

void set_485(uint8_t status){

    if( status == RE_DE_SEND ){
        gpio_put(UART_DE, 1);
        gpio_put(UART_RE, 1);
    }
    if( status == RE_DE_RECV ){
        gpio_put(UART_DE, 0);
        gpio_put(UART_RE, 0);
    }
    if( status == RE_DE_HIGHZ ){
        gpio_put(UART_DE, 0);
        gpio_put(UART_RE, 1);
    }

}

void interrupt_handler() {

}

void core1_timer(){
    while(true){
        if(habilita_recv_uart==false){
            timer_recv_uart++;
            if(timer_recv_uart==100){
                timer_recv_uart=0;
                habilita_recv_uart=true;
                set_485(RE_DE_RECV);
            }
        }
        sleep_ms(1);
    }
}

void rs485_communication() {
    uart_read_blocking(UART_ID, (uint8_t *)command, 8);
    fim_de_comunicacao = true;  
}

uint16_t crc16_modbus(uint8_t *c, uint8_t len){

    uint16_t crc = 0xFFFF;

    for( size_t i=0; i < len; i++ ){

        crc ^= c[i];
        for( uint8_t j=0; j < 8; j++ ){
            if(crc & 0x0001){
                crc >>= 1;
                crc ^= 0xA001;
            }else{
                crc >>= 1;
            }
        }
    }
  return crc;
}

bool chek_crc16_modbus(){
    bool ret = false;
    
    uint8_t crc[4];

    uint8_t H=0;
    uint8_t L=0;

    for( int i=0; i < 6; i++ ){
        cmd_crc[i] = command[i];
    }
        crc[0] = command[6];
        crc[1] = command[7];
   

uint16_t cmp_crc = crc16_modbus(cmd_crc, 6);

    H = (cmp_crc>>8) & 0xFF;
    L = cmp_crc & 0xFF;

if( (L == crc[0]) && (H == crc[1]) ){
    ret = true;
}else{
    ret = false;
}

return ret;

}

void set_crc16_modbus(){
    
    uint8_t crc[4];

    uint8_t H=0;
    uint8_t L=0;
    uint16_t cmp_crc = 0;

    for( size_t i=0; i < 5; i++ ){
        cmd_crc[i] = response[i];
    }

    cmp_crc = crc16_modbus(cmd_crc, 5);
    H = (cmp_crc>>8) & 0x00FF;
    L = cmp_crc & 0x00FF;

    response[5]=L;
    response[6]=H;

}

int main() {    
    stdio_init_all();

    // Configura a frequência desejada (em Hz)
    uint32_t desired_frequency = 200000000; // Exemplo: 200 MHz
    // Configura o sistema para usar a nova frequência
    bool clk_ok = false;
    clk_ok = set_sys_clock_khz(desired_frequency / 1000, true);

    // Inicialização dos pinos
    // Inicializar o pino do LED
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    gpio_init(INPUT_PIN);
    gpio_set_dir(INPUT_PIN, GPIO_IN);

    gpio_init(OUTPUT_PIN);
    gpio_set_dir(OUTPUT_PIN, GPIO_OUT);

    gpio_init(UART_RE);
    gpio_set_dir(UART_RE, GPIO_OUT);
    gpio_put(UART_RE, 0);//Inicia como recebimento

    gpio_init(UART_DE);
    gpio_set_dir(UART_DE, GPIO_OUT);
    gpio_put(UART_DE, 0);//Inicia como recebimento

    //set_485(RE_DE_RECV);

    // Configuração do UART para RS485
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    uart_set_hw_flow(UART_ID,false,false);
    // Configura formato
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);

    // Habilitar interrupção de recebimento da uart
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;

    // Configurar função de interrupção de uart
    irq_set_exclusive_handler(UART_IRQ, rs485_communication);
    irq_set_enabled(UART_IRQ, true);

    // Agora habilita a uart para interrupção, somente recebimento
    uart_set_irq_enables(UART_ID, true, false);

    // Certifica que frequencia configurada foi correta
    if(clk_ok == true){
        toggle_led();
    }

    // Inicializar o núcleo
    multicore_launch_core1(core1_timer);

    // Configura inerrupção de entrada digital
    gpio_set_irq_enabled(INPUT_PIN, GPIO_IRQ_EDGE_RISE, true);
    gpio_set_irq_enabled_with_callback(INPUT_PIN, GPIO_IRQ_EDGE_RISE, true, &interrupt_handler);

    // Mantenha o programa principal em execução
    while (1) {
    // rs485_communication();
    tight_loop_contents();

    //Depois de ler RX da porta serial, trata comandos.
    // if( (command[0] == ID_DEVICE) && (chek_crc16_modbus() == true ) ){
    if( (fim_de_comunicacao == true) ){
        if((command[0] != ID_DEVICE)){
            set_485(RE_DE_HIGHZ);
            habilita_recv_uart = false;
            fim_de_comunicacao = false;
            limpa_buffer();
        }else{
            switch(command[3]){
                case 1:
                
                set_485(RE_DE_SEND);
                sleep_ms(100);

                response[0] = ID_DEVICE;// ID do device
                response[1] = command[1];// Comando
                response[2] = 0x02; // Numeros de bytes enviados
                response[3] = 0x01; // Valor de teste que representa um registrador  aser lido
                response[4] = 0x01; // Valor de teste que representa um valor de entrada digital ou analógica

                set_crc16_modbus();

                while( uart_is_writable(UART_ID) == false ){;}
                uart_write_blocking(UART_ID,(uint8_t *)response, 7);
                sleep_ms(120);
                set_485(RE_DE_RECV);
                toggle_led_fast();
                break;
                
            }
        }
        limpa_buffer();
        fim_de_comunicacao = false;
    }else {
        limpa_buffer();
        // sleep_ms(1000);
        // toggle_led_fast();
    }

    // if((command[0] != ID_DEVICE) && (habilita_recv_uart == true) ){
    //         limpa_buffer();
    //         toggle_led_fast();
    //         habilita_recv_uart = false;
    //     }
    
    }

    return 0;
}
