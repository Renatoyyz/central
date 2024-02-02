import serial
import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

global loc
global pulsos_encoder
global milimetros

send_485 = 1
receive_485 = 0


GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)

#GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17,send_485)

# Inicializa a porta serial
ser = serial.Serial(
    #port='/dev/ttyUSB0',  # Porta serial padrão no Raspberry Pi 4
    port='/dev/ttyS0',  # Porta serial padrão no Raspberry Pi 4
    baudrate=9600,       # Taxa de baud
    timeout=1,            # Timeout de leitura
    xonxoff=False,         # Controle de fluxo por software (XON/XOFF)
    #rtscts=True
)

# Função para enviar e receber dados
def enviar_e_receber_dados(id_byte, comando_byte):
    # Configuração para envio
    dados_recebidos = None
    GPIO.output(17,send_485)
    # time.sleep(1)
    # ser.flush()
    # while ser.writable() == False:
    #     pass
    ser.write([id_byte, comando_byte])
    ser.flush()
    GPIO.output(17,receive_485)
    # time.sleep(1)
    while ser.readable()==False:
        pass
    dados_recebidos = ser.read_until()
    # ser.flush()
    return dados_recebidos

# Método para salvar os dados em um arquivo CSV
def salvar_em_csv(dados_recebidos):
    with open('dados.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # O dado recebido é convertido para string e as aspas duplas são removidas antes de salvar
        caracteres = "\n\'\"[]"
        tabela = str.maketrans("","",caracteres)
        dados_recebidos = dados_recebidos.translate(tabela)
        csv_writer.writerow([dados_recebidos])

# Método para salvar os dados em um arquivo CSV
def salvar_confi(dados_recebidos):
    with open('conf.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # O dado recebido é convertido para string e as aspas duplas são removidas antes de salvar
        caracteres = "\n\'\"[]"
        tabela = str.maketrans("","",caracteres)
        dados_recebidos = dados_recebidos.translate(tabela)

        csv_writer.writerow([dados_recebidos])


def ler_config(nome_arquivo='conf.csv'):
    try:
        # Abre o arquivo CSV no modo de leitura
        with open(nome_arquivo, 'r', newline='') as arquivo_csv:
            # Cria um objeto reader
            leitor_csv = csv.reader(arquivo_csv)

            # Lê a primeira linha do arquivo
            linha = next(leitor_csv, None)

            # Verifica se a linha não está vazia
            if linha:
                # Retorna o valor da primeira célula como uma string
                # Divida a string usando o ponto e vírgula como delimitador
                partes = linha[0].split(';')
                # Converta as partes para números inteiros
                numero1 = int(partes[0])
                numero2 = int(partes[1])
                return numero1, numero2
            else:
                print(f'O arquivo {nome_arquivo} está vazio.')
                return None, None
    except FileNotFoundError:
        print(f'O arquivo {nome_arquivo} não foi encontrado.')
        return None

try:
    enviar_e_receber_dados(0x01, 1)
    ser.flush()
    while True:
        # Exemplo: envia ID 0x01, comando 0xAA e recebe dados
        id_enviar = 0x01

        comando_enviar = input("Digite Comando\n")
        if comando_enviar != "":
            dados_recebidos = enviar_e_receber_dados(id_enviar, int(comando_enviar))

        # Exibe os dados recebidos
        if dados_recebidos != b'' :
            try:
                loc = dados_recebidos
                #loc = int(loc)
            except:
                loc = None
                print(f'Valor inconsistente: {loc}')
                continue
            if loc != None:
                if int(comando_enviar) == 1:
                    print(f'{loc}')
                    loc=b''
                
            time.sleep(1)  # Aguarda 1 segundo antes de enviar novamente
        else:
            time.sleep(1)  # Aguarda 1 segundo antes de enviar novamente

except KeyboardInterrupt:
    pass

finally:
    ser.close()
