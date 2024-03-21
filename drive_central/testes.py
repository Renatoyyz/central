from Controller.ModbusRTU import RTU485
import serial
from time import sleep

ser = serial.Serial(
    port='/dev/ttyUSB0',  # Porta serial padrão no Raspberry Pi 4
    # port='/dev/ttyS0',  # Porta serial padrão no Raspberry Pi 4
    baudrate=9600,       # Taxa de baud
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=1,            # Timeout de leitura
    #xonxoff=False,         # Controle de fluxo por software (XON/XOFF)
    #rtscts=True
)

devices = {
        "mod-eda": 2,
        "mod-pta9b": 1,
        "mod-adam" : 1
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
            cmd = input("Digite a saída\n1 = out_01\n2 = out_02\n3 = out_03\n4 = out_04\n")
            if int(cmd) == 1:
               cmd = input(f"Digite 1 para ligar e 0 para desligar a saída {int(cmd)}\n") 
               retorno = rtu.set_out(do_01=int(cmd))
            if int(cmd) == 2:
               cmd = input(f"Digite 1 para ligar e 0 para desligar a saída {int(cmd)}\n") 
               retorno = rtu.set_out(do_02=int(cmd))
            if int(cmd) == 3:
               cmd = input(f"Digite 1 para ligar e 0 para desligar a saída {int(cmd)}\n") 
               retorno = rtu.set_out(do_03=int(cmd))
            if int(cmd) == 4:
               cmd = input(f"Digite 1 para ligar e 0 para desligar a saída {int(cmd)}\n") 
               retorno = rtu.set_out(do_04=int(cmd))
            
            print(f'Modulo adam: {retorno}\n')
        if cmd == "4":
            retorno = rtu.mod_eda() #rtu.enviar_e_receber_dados(int(cmd))
            print(f'Modulo ead: {retorno}\n')
            sleep(1)
            retorno = rtu.temp_pta9b()
            print(f'Modulo ptb9: {retorno}\n')
        
    except:
        continue
rtu._serial.close()

