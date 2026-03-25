from machine import Pin, PWM
from time import sleep

notas = [27.4, 29.1, 30.8, 32.7, 36.6, 36.9, 39.1, 41.4, 43.6, 46, 49.1, 52, 55.3, 58.7, 61.8]

buzzer1 = PWM(Pin(0, Pin.OUT))
buzzer2 = PWM(Pin(2, Pin.OUT))
buzzer3 = PWM(Pin(4, Pin.OUT))

# Função para tocar nota
def tocar_nota(frequencia, duracao, buzzer):
    if buzzer == 1:
        buzzer1.freq(frequencia)  # Define a frequência
        buzzer1.duty(512)         # Define o volume (50% do ciclo de trabalho)
        sleep(duracao)
        buzzer1.duty(0)           # Desliga o som
    elif buzzer == 2:
        buzzer2.freq(frequencia)  # Define a frequência
        buzzer2.duty(512)         # Define o volume (50% do ciclo de trabalho)
        sleep(duracao)
        buzzer2.duty(0)           # Desliga o som
    else:
        buzzer3.freq(frequencia)  # Define a frequência
        buzzer3.duty(512)         # Define o volume (50% do ciclo de trabalho)
        sleep(duracao)
        buzzer3.duty(0)           # Desliga o som

def tocar_acorde(acorde):
    if acorde == "G#m":
        buzzer1.freq(417)
        buzzer2.freq(497)
        buzzer3.freq(625)
        buzzer1.duty(512)
        buzzer2.duty(512)
        buzzer3.duty(512)
        sleep(0.5)
        buzzer1.duty(0)
        buzzer2.duty(0)
        buzzer3.duty(0)
    elif acorde == "E":
        buzzer1.freq(330)
        buzzer2.freq(417)
        buzzer3.freq(625)
        buzzer1.duty(497)
        buzzer2.duty(512)
        buzzer3.duty(512)
        sleep(0.5)
        buzzer1.duty(0)
        buzzer2.duty(0)
        buzzer3.duty(0)

# Exemplo de sons
while True:
    tocar_nota(300, 0.2, 1)  # Tom 1
    tocar_nota(350, 0.2, 2)  # Tom 2
    tocar_nota(400, 0.2, 3)  # Tom 3
    sleep(1)
    tocar_acorde("G#m")
    sleep(1)
    tocar_acorde("E")
    sleep(1)