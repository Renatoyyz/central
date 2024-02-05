import time
import threading
import math
from typing import Any
import RPi.GPIO as GPIO

from Controller.IO import InOut

class RTU485(threading.Thread):
    def __init__(self,serial, devices_address=[], mode = 'rtu'):
        threading.Thread.__init__(self)

        self._serial = serial
        self._devices_address = devices_address
        self._mode = mode

        self.in_out = InOut()

    def crc16_modbus(self, data):
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if (crc & 0x0001):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

# # Dados de entrada em hexadecimal
# data_hex = "02 03 00 00 00 01"
# data_bytes = bytes.fromhex(data_hex)

# # Cálculo do CRC
# crc_result = crc16_modbus(data_bytes)

# # Exibição do resultado em hexadecimal
# print(f"CRC-16/MODBUS: {crc_result:04X}")


    def enviar_e_receber_dados(self, comando_byte):
        dados_recebidos = None
        self.in_out.re_de_485(self.in_out.SEND_485)

        self._serial.write([self._devices_address[0], comando_byte])
        self._serial.flush()
        self.in_out.re_de_485(self.in_out.RECV_485)

        while self._serial.readable()==False:
            pass

        dados_recebidos = self._serial.read_until()
        # ser.flush()
        return dados_recebidos
    
    def temp_pta9b(self):
        dados_recebidos = None
        self.in_out.re_de_485(self.in_out.SEND_485)

        hex_text = f"0{self._devices_address[0]}0300010001" # Comando para leitura de resistencia do Modulo PTA9B

        bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa

        crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

        parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
        parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

        # Repete-se os comandos em decimal com os devidos bytes de CRC
        self._serial.write([self._devices_address[0], 3,0,1,0,1,parte_inferior,parte_superior])
        self._serial.flush()
        self.in_out.re_de_485(self.in_out.RECV_485)

        while self._serial.readable()==False:
            pass
        dados_recebidos = self._serial.read_until()
        try:
            # "01030207f0ba30"
            dados_recebidos = dados_recebidos.hex()
            hex_text = dados_recebidos[0:2]+dados_recebidos[2:4]+dados_recebidos[4:6]+dados_recebidos[6:8]+dados_recebidos[8:10]
            bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa
            crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

            parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
            parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

            superior_crc = int(dados_recebidos[12:14],16) # Transforma de hexa para int
            inferior_crc = int(dados_recebidos[10:12],16) # Transforma de hexa para int

            if parte_superior == superior_crc and parte_inferior == inferior_crc:
                dados_recebidos = dados_recebidos[6:10]
                dados_recebidos = int(dados_recebidos,16)/10
                return dados_recebidos
            else:
                return -1
        except:
            return -1 # Indica erro de alguma natureza....
        
    def crc16_retorno(self,data):
        pass
    
if __name__ == '__main__':
    pass
