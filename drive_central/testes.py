from Controller.ModbusRTU import RTU485
import serial

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
        "mod-da-01": 2,
        "mod-pta9b": 1
}

rtu = RTU485(ser, devices_address=devices)

cmd = ""
#01030204017b44
while(cmd.upper() != "Q"):
    cmd = input("Digitar comando\n")

    try:
        retorno1 = rtu.enviar_e_receber_dados(int(cmd))
        retorno = rtu.temp_pta9b()
        if retorno != -1:
            print(f'Modulo ed-ea: {retorno1}\nModulo Temperatura: {retorno}')
        else:
            print("Erro de comunicação com Módulo de temperatura\n")
    except:
        continue
rtu._serial.close()

