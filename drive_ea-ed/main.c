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

#define UART_ID uart0
#define BAUD_RATE 9600
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE

#define UART_RE_DE 2
#define RE_DE_SEND 1
#define RE_DE_RECV 0

#define UART_TX_PIN 0
#define UART_RX_PIN 1


#define PISTAO_RECUADO 0
#define PISTAO_AVANCADO 1

//Constante para definir um delay para o inicio do avanço ou recuo do pistão
#define DELAY_AV_RE 1000

char info_response[40];
volatile uint32_t cnt_encoder_role = 0;
char flag_pistao = PISTAO_RECUADO;
char command[2];

//
#define STATUS_HAB 1
#define STATUS_DESABI 2
#define STATUS_DESATI 0

char inicia_para_moviento_avanco = STATUS_DESATI;
char inicia_para_moviento_recuo = STATUS_DESATI;
bool status_encoder = false;
bool movimento_encoder = true;

volatile uint32_t cnt_timer_avanco = 0;
volatile uint32_t cnt_timer_recuo = 0;

volatile uint32_t encoder_role_avanco = 0;
volatile uint32_t encoder_role_recuo = 0;

void toggle_led();
void toggle_led_fast();

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

void interrupt_handler() {

    cnt_encoder_role += 1;
    movimento_encoder = true;
    if( cnt_encoder_role > 1000000000 ){
        cnt_encoder_role=0;
    }
}

void core1_timer(){
    while(true){
        sleep_ms(1);
    }
}

volatile uint32_t pistao(bool atv){
        gpio_put(OUTPUT_PIN, atv);
        if( atv == 1 ){
            flag_pistao = PISTAO_AVANCADO;
            snprintf(info_response, sizeof(info_response), "%s", "-1\n");// -1 indica, para o mestre, avanço.
            uart_puts(UART_ID, info_response);
        }else if( atv == 0 ){
            flag_pistao = PISTAO_RECUADO;
            snprintf(info_response, sizeof(info_response), "%s", "-2\n");// -2 indica, para o mestre, recuo.
            uart_puts(UART_ID, info_response);
        }
        return cnt_encoder_role;// retorna valor do encoder
}

void rs485_communication() {

    while (uart_is_readable(UART_ID)) {    
        uart_read_blocking(UART_ID, (uint8_t *)command, sizeof(command));
    }
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

    gpio_init(UART_RE_DE);
    gpio_set_dir(UART_RE_DE, GPIO_OUT);
    gpio_put(UART_RE_DE, RE_DE_RECV);//Inicia como recebimento

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
    if((command[0] == 0x01)){
        switch(command[1]){
            case 1:
            char response[40];
            gpio_put(UART_RE_DE, RE_DE_SEND);
            sleep_ms(100);
            while( uart_is_writable(UART_ID) == false ){;}
            cnt_encoder_role = 123; //zera o contador de encoder
            snprintf(response, sizeof(response), "%s;%ld", "Renato Oliveira",cnt_encoder_role);
            // uart_puts(UART_ID, info_response);
            // uart_write_blocking(UART_ID,(uint8_t *)response, strlen(response));
            for( int s=0; s < strlen(response); s++ ){
                while( uart_is_writable(UART_ID) == false ){;}
                uart_putc(UART_ID,response[s]);
                if(response[s]=='\n'){
                    break;
                }
            }
            sleep_ms(100);
            gpio_put(UART_RE_DE, RE_DE_RECV);
            break;
            case 2:
            toggle_led_fast();
            break;

            default:
            toggle_led();
            
        }
        //Limpa buffer de comando
        for ( int i=0;i<strlen(command);i++ ){
                command[i]=0;
        }
        
        }
    }

    return 0;
}
