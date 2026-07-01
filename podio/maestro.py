import network
import espnow
from umqtt.simple import MQTTClient
import json
import time
import ubinascii

# ==========================================
# CONFIGURAÇÕES
# ==========================================
WIFI_SSID = "NOME_DO_SEU_WIFI_AQUI"
WIFI_SENHA = "SENHA_DO_SEU_WIFI_AQUI"
BROKER = "broker.hivemq.com"
TOPICO_PARTITURA = b"projeto/orquestra/partitura"

# ==========================================
# 1. CONEXÃO WI-FI E ESP-NOW
# ==========================================
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(WIFI_SSID, WIFI_SENHA)

print("Conectando o Maestro ao Wi-Fi...")
while not sta.isconnected():
    time.sleep(0.5)

print(f"Maestro online! Canal Wi-Fi: {sta.config('channel')}")

# Inicia ESP-NOW e configura o Broadcast (enviar para todos os tocadores ao redor)
e = espnow.ESPNow()
e.active(True)
peer_broadcast = b'\xFF\xFF\xFF\xFF\xFF\xFF'
e.add_peer(peer_broadcast)

# ==========================================
# 2. CONEXÃO MQTT
# ==========================================
# ID único para o maestro
id_maestro = b"maestro_" + ubinascii.hexlify(sta.config('mac'))
client = MQTTClient(id_maestro, BROKER)

try:
    client.connect()
    print("Maestro conectado ao servidor MQTT (Internet).")
except Exception as erro:
    print(f"Erro ao conectar no MQTT: {erro}")

# ==========================================
# 3. LENDO O ARQUIVO JSON
# ==========================================
def ler_partituras_do_arquivo(caminho_arquivo="partituras.json"):
    print(f"Lendo as partituras do arquivo '{caminho_arquivo}'...")
    try:
        # Abre o arquivo no modo de leitura ("r")
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            # Converte o texto JSON em um dicionário Python
            todas_as_partituras = json.load(arquivo)
            return todas_as_partituras
    except OSError:
        print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado no ESP32!")
        return None
    except ValueError:
        print(f"ERRO: O arquivo '{caminho_arquivo}' tem algum erro de formatação (JSON inválido)!")
        return None

# ==========================================
# 4. FUNÇÃO PARA COMANDAR A ORQUESTRA
# ==========================================
def reger_orquestra(nome_da_musica, bpm):
    # 1. Carrega todas as músicas do arquivo
    acervo = ler_partituras_do_arquivo()
    
    if acervo is None or nome_da_musica not in acervo:
        print(f"Música '{nome_da_musica}' não encontrada no arquivo JSON!")
        return
    
    # 2. Prepara o pacote (payload) que será enviado para os tocadores
    pacote_musical = {
        "bpm": bpm,
        "musica": nome_da_musica,
        "partitura": acervo[nome_da_musica]
    }
    
    # 3. Envia o arquivo da música pela internet (MQTT)
    print(f"\n[1] Enviando a partitura de '{nome_da_musica}' pelo MQTT...")
    payload_json = json.dumps(pacote_musical)
    client.publish(TOPICO_PARTITURA, payload_json.encode('utf-8'))
    
    # 4. Dá 5 segundos para todos os Tocadores baixarem e carregarem a música
    print("[2] Aguardando os tocadores fazerem o download e se prepararem (5 segundos)...")
    for i in range(5, 0, -1):
        print(f"... {i}")
        time.sleep(1)
    
    # 5. O "Tiro de Largada" direto via rádio (ESP-NOW) - Baixíssima latência!
    print("\n[3] 🎵 Enviando comando START via ESP-NOW! A Orquestra vai começar!")
    e.send(peer_broadcast, b'START')
    
    print("Regência concluída!")

# ==========================================
# 5. EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    # Aqui você escolhe qual música do seu partituras.json você quer tocar e o BPM
    # Exemplo: tocando 'tetris' a 140 BPM
    reger_orquestra("tetris", 140)