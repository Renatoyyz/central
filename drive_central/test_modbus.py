def crc16_modbus(data):
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

hex_text = f"0203020101" # Comando para leitura de resistencia do Modulo PTA9B
bytes_hex = bytes.fromhex(hex_text) # Transforma em hexa
crc_result = crc16_modbus(bytes_hex) # Retorna o CRC
parte_superior = (crc_result >> 8) & 0xFF  # Desloca 8 bits para a direita e aplica a máscara 0xFF
parte_inferior = crc_result & 0xFF        # Aplica a máscara 0xFF diretamente
print(crc_result)