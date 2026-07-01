from machine import Pin, PWM
from time import sleep
import ubinascii
import network
import espnow
from umqtt.simple import MQTTClient
import json

# ==========================================
# CONFIGURAÇÕES DE REDE E SERVIDOR
# ==========================================
WIFI_SSID = "NOME_DO_SEU_WIFI_AQUI"
WIFI_SENHA = "SENHA_DO_SEU_WIFI_AQUI"

BROKER_MQTT = "broker.hivemq.com"
TOPICO_PARTITURA = b"projeto/orquestra/partitura"
TOPICO_COMANDO = b"projeto/orquestra/comando"

# Variáveis globais para guardar a música recebida pela internet
partitura_baixada = None
bpm_baixado = 120

# ==========================================
# 1. LIMPEZA DE SEGURANÇA (Garante que os pinos começam livres)
# ==========================================
pinos = [Pin(0, Pin.OUT), Pin(2, Pin.OUT), Pin(5, Pin.OUT)]
for p in pinos:
    try:
        PWM(p).deinit()
    except:
        pass

buzzers_ativos = []

# ==========================================
# 2. DICIONÁRIO DE NOTAS
# ==========================================
notas_padrao = {
    'C3': 131, 'C#3': 139, 'D3': 147, 'D#3': 156, 'E3': 165, 'F3': 175,
    'F#3': 185, 'G3': 196, 'G#3': 208, 'A3': 220, 'A#3': 233, 'B3': 247,
    'C4': 262, 'C#4': 277, 'D4': 294, 'D#4': 311, 'E4': 330, 'F4': 349,
    'F#4': 370, 'G4': 392, 'G#4': 415, 'A4': 440, 'A#4': 466, 'B4': 494,
    'C5': 523, 'C#5': 554, 'D5': 587, 'D#5': 622, 'E5': 659, 'F5': 698,
    'F#5': 740, 'G5': 784, 'G#5': 831, 'A5': 880, 'A#5': 932, 'B5': 988
}

# ==========================================
# 3. FUNÇÕES DE MÚSICA (A MÁGICA ESTÁ AQUI)
# ==========================================
def tocar_passo(notas, tempos, bpm):
    global buzzers_ativos
    segundos_por_batida = 60.0 / bpm
    duracao_segundos = tempos * segundos_por_batida

    if notas == "pausa":
        sleep(duracao_segundos)
        return
        
    for i in range(len(notas)):
        if i < 3: 
            nota = notas[i]
            if nota in notas_padrao:
                # Aloca o timer apenas na hora de tocar
                buzzer = PWM(pinos[i], freq=notas_padrao[nota], duty=300)
                buzzers_ativos.append(buzzer)

    # Mantém a nota tocando pelo tempo determinado
    sleep(duracao_segundos)

    # DESTRÓI os buzzers ativos. Devolve o timer pro ESP32!
    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except:
            pass
            
    buzzers_ativos.clear()
    sleep(0.02) 

def reproduzir_musica(partitura, bpm):
    print(f"Iniciando música a {bpm} BPM...")
    for passo in partitura:
        # passo[0] são as notas (ex: ["C4", "C3"]), passo[1] é o tempo (ex: 1)
        tocar_passo(passo[0], passo[1], bpm)
    print("Música finalizada!")

# ==========================================
# 4. CONFIGURAÇÃO DE REDE (Wi-Fi + ESP-NOW + MQTT)
# ==========================================
# 4.1 Conectando ao Wi-Fi
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(WIFI_SSID, WIFI_SENHA)

print("Conectando ao Wi-Fi...")
while not sta.isconnected():
    sleep(0.5)
print(f"Conectado! Canal do Wi-Fi: {sta.config('channel')}")

# 4.2 Iniciando o ESP-NOW (ele herda o canal do Wi-Fi)
e = espnow.ESPNow()
e.active(True)

# 4.3 Configurando o MQTT para baixar as partituras
def recepcao_mqtt(topico, mensagem):
    global partitura_baixada, bpm_baixado
    print("\n[MQTT] Nova mensagem recebida do Maestro!")
    try:
        dados = json.loads(mensagem.decode('utf-8'))
        partitura_baixada = dados.get("partitura")
        bpm_baixado = dados.get("bpm", 120)
        musica_nome = dados.get("musica", "Desconhecida")
        print(f"-> Música '{musica_nome}' carregada na memória com sucesso!")
    except Exception as erro:
        print("[MQTT] Erro ao ler a partitura:", erro)

id_cliente = b"tocador_" + ubinascii.hexlify(sta.config('mac'))

client = MQTTClient(id_cliente, BROKER_MQTT)
client.set_callback(recepcao_mqtt)
client.connect()
client.subscribe(TOPICO_PARTITURA)
print("Inscrito no MQTT. Aguardando partituras da internet...")

# ==========================================
# 5. EXECUÇÃO PRINCIPAL
# ==========================================
print("\n🎵 Tocador 100% pronto e escutando rádio (ESP-NOW) para o START...")

try:
    while True:
        # 1. Verifica rapidinho se chegou partitura pelo MQTT
        client.check_msg()
        
        # 2. Ouve o rádio ESP-NOW para o gatilho de sincronia (START)
        host, msg = e.irecv(timeout_ms=10) 
        
        if msg:
            if msg == b'START':
                if partitura_baixada:
                    print(f"\n[ESP-NOW] Comando START recebido! Tocando a {bpm_baixado} BPM...")
                    reproduzir_musica(partitura_baixada, bpm_baixado)
                    print("Fim da música. Aguardando novas ordens...")
                else:
                    print("\n[ESP-NOW] Maestro mandou tocar, mas nenhuma partitura foi recebida ainda!")

except KeyboardInterrupt:
    print("\nVocê apertou Stop. Parando a música e desligando...")
except Exception as erro_geral:
    print(f"\nErro no código: {erro_geral}")
finally:
    # Caso o código seja interrompido, limpamos os pinos com segurança
    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except:
            pass
    print("Pronto! Timers liberados com sucesso. Código limpo.")