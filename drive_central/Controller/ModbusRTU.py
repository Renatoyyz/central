import time
import threading
import math
from typing import Any
import RPi.GPIO as GPIO

from .IO import InOut

class RTU485(threading.Thread):
    def __init__(self,serial, devices_address={}, mode = 'rtu'):
        threading.Thread.__init__(self)

        self._serial = serial
        self._devices_address = devices_address
        self._mode = mode

        self._out = [0,0,0,0]

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
    
    def mod_eda(self):
        
        dados_recebidos = None
        self.in_out.re_de_485(self.in_out.SEND_485)

        id_loc = hex(self._devices_address['mod-eda'])[2:]
        id_loc = id_loc.zfill(2).upper()

        hex_text = f"{id_loc}0300010002" # Comando para leitura de resistencia do Modulo PTA9B

        bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa

        crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

        parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
        parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

        id_loc = self._devices_address['mod-eda']

        # Repete-se os comandos em decimal com os devidos bytes de CRC
        self._serial.write([id_loc, 3,0,1,0,2,parte_inferior,parte_superior])
        # self._serial.flush()
        self.in_out.re_de_485(self.in_out.RECV_485)

        while self._serial.readable()==False:
            pass
        dados_recebidos = self._serial.read(7)
        # self._serial.flush()
        try:
            # "01030207f0ba30"
            # "020302020303bd23"
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
                dados_recebidos = int(dados_recebidos)
                # time.sleep(0.5)
                return dados_recebidos
            else:
                return -1
        except:
            return -1 # Indica erro de alguma natureza....
        
    def set_out(self, do_01=None, do_02=None, do_03=None, do_04=None):
        if do_01 != None:
            self._out[3]=do_01
        if do_02 != None:
            self._out[2]=do_02
        if do_03 != None:
            self._out[1]=do_03
        if do_04 != None:
            self._out[0]=do_04
        return self.adam_wp9038()


    def adam_wp9038(self):
        
        dados_recebidos = None
        self.in_out.re_de_485(self.in_out.SEND_485)

        id_loc = hex(self._devices_address['mod-adam'])[2:]
        id_loc = id_loc.zfill(2).upper()

        out_loc = ''.join(str(bit) for bit in self._out)
        out_loc = int(out_loc, 2)
        out_val = out_loc

        out_loc = hex(out_loc)[2:]
        out_loc = out_loc.zfill(2).upper()

        hex_text = f"{id_loc} 0f 00 00 00 04 01 {out_loc}"
        #01 0F 00 00 00 04 01 03
        bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa

        crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

        parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
        parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

        id_loc = self._devices_address['mod-adam']

        # Repete-se os comandos em decimal com os devidos bytes de CRC
        # self._serial.flush()
        self._serial.write([id_loc,0x0f,0,0,0,4,1,out_val,parte_inferior,parte_superior])
        self._serial.flush()
        self.in_out.re_de_485(self.in_out.RECV_485)
        time.sleep(0.2)

        while self._serial.readable()==False:
            pass
        dados_recebidos = self._serial.read(8)
        try:
            # "01030207f0ba30"
            # "020302020303bd23"
            #00 00 04 54 08
            dados_recebidos = dados_recebidos.hex()
            hex_text = dados_recebidos[0:2]+dados_recebidos[2:4]+dados_recebidos[4:6]+dados_recebidos[6:8]+dados_recebidos[8:10]+dados_recebidos[10:12]
            bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa
            crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

            parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
            parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

            superior_crc = int(dados_recebidos[14:16],16) # Transforma de hexa para int
            inferior_crc = int(dados_recebidos[12:14],16) # Transforma de hexa para int

            if parte_superior == superior_crc and parte_inferior == inferior_crc:
                dados_recebidos = dados_recebidos[14:16]
                dados_recebidos = int(dados_recebidos)
                # time.sleep(0.5)
                return dados_recebidos
            else:
                return -1
        except:
            return -1 # Indica erro de alguma natureza....
        
    def broadcast(self):
        
        dados_recebidos = None
        self.in_out.re_de_485(self.in_out.SEND_485)

        id_loc = "00" # hex(self._devices_address['mod-eda'])[2:]
        id_loc = id_loc.zfill(2).upper()

        hex_text = f"{id_loc}0600640001"

        bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa

        crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

        parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
        parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

        id_loc = 0 # self._devices_address['mod-adam']

        # Repete-se os comandos em decimal com os devidos bytes de CRC
        self._serial.write([id_loc, 6,0,0x64,0,1,parte_inferior,parte_superior])
        self._serial.flush()
        self.in_out.re_de_485(self.in_out.RECV_485)

        while self._serial.readable()==False:
            pass
        dados_recebidos = self._serial.read(21)
        # self._serial.flush()
        try:
            # "01030207f0ba30"
            # "020302020303bd23"
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
                dados_recebidos = int(dados_recebidos)
                # time.sleep(0.5)
                return dados_recebidos
            else:
                return -1
        except:
            return -1 # Indica erro de alguma natureza....
        

    def temp_pta9b(self):
        dados_recebidos = None
        self.in_out.re_de_485(self.in_out.SEND_485)

        id_loc = hex(self._devices_address['mod-pta9b'])[2:]
        id_loc = id_loc.zfill(2).upper()

        hex_text = f"{id_loc}0300010001" # Comando para leitura de resistencia do Modulo PTA9B

        bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa

        crc_result = self.crc16_modbus(bytes_hex) # Retorna o CRC

        parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
        parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente

        id_loc = self._devices_address['mod-pta9b']

        # Repete-se os comandos em decimal com os devidos bytes de CRC
        self._serial.write([id_loc, 3,0,1,0,1,parte_inferior,parte_superior])
        self._serial.flush()
        self.in_out.re_de_485(self.in_out.RECV_485)

        while self._serial.readable()==False:
            pass
        dados_recebidos = self._serial.read(8)
        # self._serial.flush()
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
                # time.sleep(0.5)
                return dados_recebidos
            else:
                return -1
        except:
            return -1 # Indica erro de alguma natureza....
        
        
    def crc16_retorno(self,data):
        pass
    
if __name__ == '__main__':
    pass
