import RPi.GPIO as GPIO

class InOut:
    def __init__(self):

        # Constantes
        self.SEND_485 = 1
        self.RECV_485 = 0
        self.PIN_RE_DE = 17

        GPIO.setmode(GPIO.BCM) 
        GPIO.setwarnings(False)

        GPIO.setup(self.PIN_RE_DE, GPIO.OUT)# Configura para controle DE/RE
        self.re_de_485(self.SEND_485)# Inicia como envio de dados

    def re_de_485(self, val):
        GPIO.output(self.PIN_RE_DE, val)