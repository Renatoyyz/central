from Controller.ModbusRTU import RTU485
import serial
from time import sleep

ser = serial.Serial(
    #port='/dev/ttyUSB0',  # Porta serial padrão no Raspberry Pi 4
    port='/dev/ttyS0',  # Porta serial padrão no Raspberry Pi 4
    baudrate=9600,       # Taxa de baud
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=1,            # Timeout de leitura
    xonxoff=False,         # Controle de fluxo por software (XON/XOFF)
    #rtscts=True
)
devices = {
        "mod-eda": 2,
        "mod-pta9b": 1
}

rtu = RTU485(ser, devices_address=devices)

cmd = ""
#01030204017b44
while(cmd.upper() != "Q"):
    cmd = input("Digitar comando\n")

    try:
        if cmd == "1":
            retorno = rtu.mod_eda() #rtu.enviar_e_receber_dados(int(cmd))
            print(f'Modulo ead: {retorno}\n')
        if cmd == "2":
            retorno = rtu.temp_pta9b()
            print(f'Modulo ptb9: {retorno}\n')
        if cmd == "3":
            retorno = rtu.mod_eda() #rtu.enviar_e_receber_dados(int(cmd))
            print(f'Modulo ead: {retorno}\n')
            sleep(1)
            retorno = rtu.temp_pta9b()
            print(f'Modulo ptb9: {retorno}\n')
        
    except:
        continue
rtu._serial.close()

