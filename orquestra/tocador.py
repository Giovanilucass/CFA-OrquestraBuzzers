import network
import time
import json
import gc
import machine
import ubinascii
from machine import Pin, PWM
from umqtt import MQTTClient

# ==========================================
# 1. CONFIGURAÇÕES DE REDE E MQTT
# ==========================================
WIFI_SSID = "lab8"
WIFI_PASSWORD = "lab8arduino"

BROKER_MQTT = "broker.hivemq.com"

id_hardware = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
CLIENT_ID = f"musico_{id_hardware}"

print(f"Iniciando tocador com ID Único: {CLIENT_ID}")

TOPICO_PARTITURA = b"projeto/orquestra/partitura"
TOPICO_COMANDO = b"projeto/orquestra/comando"
TOPICO_SYNC_REQ = b"projeto/orquestra/sync/req"
TOPICO_SYNC_RES = b"projeto/orquestra/sync/res"
TOPICO_SYNC_ADJ = b"projeto/orquestra/sync/adj"

offset_tempo = 0 # Guarda o ajuste calculado pelo Berkeley
deve_tocar_musica = False

def tempo_global_atual():
    # Relógio Global = Relógio de Hardware + Ajuste do Maestro
    return time.ticks_ms() + offset_tempo

# Variáveis globais para guardar a música recebida
partitura_atual = []
bpm_atual = 120

# ==========================================
# 2. LIMPEZA E CONFIGURAÇÃO DOS PINOS
# ==========================================
pinos = [Pin(0, Pin.OUT), Pin(2, Pin.OUT), Pin(5, Pin.OUT)]
for p in pinos:
    try:
        PWM(p).deinit()
    except:
        pass

buzzers_ativos = []

# ==========================================
# 3. DICIONÁRIO DE NOTAS
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
# 4. MOTOR DE ÁUDIO (À Prova de Falhas de Memória)
# ==========================================
def tocar_passo(notas, tempos, bpm):
    global buzzers_ativos
    segundos_por_batida = 60.0 / bpm
    duracao_segundos = tempos * segundos_por_batida

    if notas == "pausa":
        time.sleep(duracao_segundos)
        return
        
    for i in range(len(notas)):
        if i < 3: 
            nota = notas[i]
            if nota in notas_padrao:
                buzzer = PWM(pinos[i], freq=notas_padrao[nota], duty=300)
                buzzers_ativos.append(buzzer)

    time.sleep(duracao_segundos)

    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except:
            pass
            
    buzzers_ativos.clear()
    time.sleep(0.02) 

def reproduzir_musica():
    global partitura_atual, bpm_atual
    print(f"Tocando a {bpm_atual} BPM...")
    for passo in partitura_atual:
        # passo[0] são as notas, passo[1] é o tempo
        tocar_passo(passo[0], passo[1], bpm_atual)
    print("Música finalizada! Aguardando novas ordens...")
    
    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except Exception as e:
            print(f"Erro ao limpar PWM: {e}")
            
    print("Música finalizada e timers liberados com sucesso.")

# ==========================================
# 5. CONEXÃO WI-FI
# ==========================================
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    
    # --- LIMPEZA DE ESTADO DO WI-FI ---
    # Desliga a antena e limpa tentativas de conexão anteriores
    wlan.active(False)
    time.sleep(0.5)
    
    wlan.active(True)
    wlan.disconnect() # Garante que está desconectado antes de tentar conectar
    time.sleep(0.5)
    # ----------------------------------
    
    if not wlan.isconnected():
        print(f"Conectando à rede {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Adiciona um limite de tempo para não travar para sempre
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(0.5)
            print(".", end="")
            tentativas += 1
            
        if wlan.isconnected():
            print("\nWi-Fi Conectado! IP:", wlan.ifconfig()[0])
        else:
            print("\nErro: Tempo esgotado! Verifique o nome e a senha da rede Wi-Fi.")

# ==========================================
# 6. LÓGICA DO MQTT (Ouvido do Músico)
# ==========================================
def callback_mensagem(topico, msg):
    global partitura_atual, bpm_atual, offset_tempo
    global deve_tocar_musica
    
    topico_str = topico.decode('utf-8')
    msg_str = msg.decode('utf-8')
    
    # 1. Maestro pediu que horas são
    if topico_str == TOPICO_SYNC_REQ.decode('utf-8'):
        resposta = json.dumps({"id": CLIENT_ID, "t": time.ticks_ms()})
        cliente_mqtt.publish(TOPICO_SYNC_RES, resposta)
        print("Relógio local enviado para o Maestro.")
        
    # 2. Maestro enviou o ajuste do relógio
    elif topico_str == TOPICO_SYNC_ADJ.decode('utf-8'):
        dados = json.loads(msg_str)
        # Verifica se o ajuste de tempo é para este ESP32 específico
        if dados.get("id") == CLIENT_ID:
            offset_tempo = dados.get("offset_ms", 0)
            print(f"Relógio Global sincronizado! Offset: {offset_tempo}")

    # 3. Maestro enviou a partitura
    elif topico_str == TOPICO_PARTITURA.decode('utf-8'):
        try:
            dados = json.loads(msg_str)
            destino = dados.get("destino")
            if destino and destino != CLIENT_ID:
                print(f"Partitura ignorada para outro destino: {destino}")
                return

            bpm_atual = dados.get("bpm", 120)
            partitura_atual = dados.get("partitura", [])
            print(f"Partitura recebida para {CLIENT_ID}. Aguardando comando START...")
        except ValueError:
            print("Erro ao ler o JSON da partitura.")
            
    # 4. Maestro enviou a ordem de início agendada
    elif topico_str == TOPICO_COMANDO.decode('utf-8'):
        try:
            dados = json.loads(msg_str)
            if dados.get("comando") == "START":
                start_at = dados.get("start_at")
                deve_tocar_musica = True
                print(f"Ordem recebida! A música começará no instante global: {start_at}")
                
                # Trava o processador em um loop muito rápido até atingir a hora certa
                while tempo_global_atual() < start_at:
                    time.sleep(0.001) # Espera 1ms por ciclo
                    
                if len(partitura_atual) > 0:
                    reproduzir_musica()
        except ValueError:
            pass # Ignora mensagens fora do padrão JSON

def conectar_mqtt():
    try:
        client = MQTTClient(CLIENT_ID, BROKER_MQTT)
        client.set_callback(callback_mensagem)
        client.connect()
        # Inscreve o ESP32 nos tópicos antigos e nos novos de sincronização
        client.subscribe(TOPICO_PARTITURA)
        client.subscribe(TOPICO_COMANDO)
        client.subscribe(TOPICO_SYNC_REQ)
        client.subscribe(TOPICO_SYNC_ADJ)
        print("Conectado ao MQTT. Inscrito nos tópicos.")
        return client
    except Exception as e:
        print(f"Erro ao conectar no MQTT: {e}")
        time.sleep(5)
        import machine
        machine.reset()

# ==========================================
# 7. LOOP PRINCIPAL
# ==========================================
conectar_wifi()
cliente_mqtt = conectar_mqtt()

print("Músico posicionado. Aguardando a partitura e a batuta do maestro...")

try:
    while True:
        cliente_mqtt.check_msg() # Ouve o maestro
        
        # Se a flag de tocar música for ativada
        if deve_tocar_musica:
            deve_tocar_musica = False
            # Força a limpeza da RAM e dos processos órfãos logo após tocar
            gc.collect() 
            
except KeyboardInterrupt:
    print("\nDesconectando...")
except OSError as e:
    print("Erro de rede. Reconectando...")
finally:
    # Segurança de sempre: libera os pinos
    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except:
            pass
    cliente_mqtt.disconnect()
