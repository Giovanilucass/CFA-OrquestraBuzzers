import network
import time
import json
import gc
import machine
import ubinascii
import _thread
from machine import Pin, PWM
from typing import Any, List, Union
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

offset_tempo = 0  # Guarda o ajuste calculado pelo Berkeley

def tempo_global_atual() -> int:
    """Retorna o timestamp global em milissegundos.

    O relógio global é o contador de ticks do hardware mais o offset do maestro
    (ver `offset_tempo`). O valor retornado está em milissegundos.
    """
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
# 4. ESTADO DE EXECUÇÃO / CONTROLE (compartilhado entre threads)
# ==========================================
# A música toca em uma thread própria (_thread), enquanto a thread principal
# continua chamando client.check_msg() e pode reagir a comandos (STOP,
# VOLUME_UP, VOLUME_DOWN) que chegam pelo MQTT SEM esperar a música acabar.
DUTY_MIN = 0
DUTY_MAX = 1000
VOLUME_PASSO_PADRAO = 100

duty_atual = 300      # "volume" atual (duty cycle do PWM), compartilhado
tocando = False        # True enquanto a thread de reprodução está ativa
parar_flag = False     # sinalizado por STOP para interromper a música

# Protege buzzers_ativos e duty_atual, que são lidos/escritos tanto pela
# thread de reprodução (tocar_passo) quanto pela thread principal (ajustar_volume)
lock = _thread.allocate_lock()

# ==========================================
# 5. MOTOR DE ÁUDIO (À Prova de Falhas de Memória)
# ==========================================
def _dormir_interruptivel(duracao_ms):
    """Dorme em pequenos pedaços, checando parar_flag para poder
    interromper a nota/pausa atual quase imediatamente após um STOP."""
    global parar_flag
    passo_ms = 20
    decorrido = 0
    while decorrido < duracao_ms:
        if parar_flag:
            return True
        fatia = passo_ms if (duracao_ms - decorrido) > passo_ms else (duracao_ms - decorrido)
        time.sleep_ms(fatia)
        decorrido += fatia
    return parar_flag

def _desligar_buzzers_ativos() -> None:
    """Desliga e desaloca todos os buzzers PWM ativos.

    Esta função é thread-safe e adquire `lock` antes de modificar a lista
    compartilhada `buzzers_ativos`.
    """
    global buzzers_ativos
    lock.acquire()
    try:
        for b in buzzers_ativos:
            try:
                b.duty(0)
                b.deinit()
            except:
                pass
        buzzers_ativos.clear()
    finally:
        lock.release()

def ajustar_volume(delta):
    """Chamada pela thread principal (a partir do callback MQTT) para
    aumentar/diminuir o volume. É rápida (só mexe numa lista de até 3
    PWMs) e por isso não desincroniza a thread que está tocando a música."""
    global duty_atual
    lock.acquire()
    try:
        novo_duty = duty_atual + delta
        if novo_duty < DUTY_MIN:
            novo_duty = DUTY_MIN
        if novo_duty > DUTY_MAX:
            novo_duty = DUTY_MAX
        duty_atual = novo_duty
        for b in buzzers_ativos:
            try:
                b.duty(duty_atual)
            except:
                pass
    finally:
        lock.release()
    print(f"Volume ajustado! duty={duty_atual}")

def tocar_passo(notas: Union[str, List[str]], tempos: float, bpm: int) -> bool:
    """Toca um único passo (nota ou acorde) pela duração definida em `tempos`.

    - `notas` pode ser a string 'pausa' ou uma lista de nomes de notas (ex.: ['C4']).
    - `tempos` é o comprimento da nota em batidas (estilo quarterLength).
    - `bpm` é usado para converter batidas em milissegundos.

    Retorna True se a reprodução foi interrompida por `parar_flag`, caso contrário False.
    """
    global buzzers_ativos, duty_atual
    segundos_por_batida = 60.0 / bpm
    duracao_ms = int(tempos * segundos_por_batida * 1000)

    if notas == "pausa":
        return _dormir_interruptivel(duracao_ms)

    lock.acquire()
    try:
        for i in range(len(notas)):
            if i < 3:
                nota = notas[i]
                if nota in notas_padrao:
                    buzzer = PWM(pinos[i], freq=notas_padrao[nota], duty=duty_atual)
                    buzzers_ativos.append(buzzer)
    finally:
        lock.release()

    interrompido = _dormir_interruptivel(duracao_ms)

    _desligar_buzzers_ativos()
    time.sleep_ms(20)
    return interrompido

def reproduzir_musica() -> None:
    """Reproduz sequencialmente a `partitura_atual` global.

    Respeita `parar_flag` para interromper a reprodução. Garante que os buzzers
    sejam desligados ao sair e limpa o estado `tocando`.
    """
    global partitura_atual, bpm_atual, tocando, parar_flag
    print(f"Tocando a {bpm_atual} BPM...")
    for passo in partitura_atual:
        if parar_flag:
            break
        interrompido = tocar_passo(passo[0], passo[1], bpm_atual)
        if interrompido:
            break

    # Segurança extra: garante que nenhum buzzer fica ligado ao sair
    _desligar_buzzers_ativos()

    if parar_flag:
        print("Música interrompida por comando STOP.")
    else:
        print("Música finalizada! Aguardando novas ordens...")

    parar_flag = False
    tocando = False

def _executar_reproducao_agendada(start_at):
    """Roda em thread separada: espera o instante sincronizado combinado
    com o maestro e então toca a partitura, sem bloquear a thread
    principal (que continua escutando STOP/VOLUME via MQTT)."""
    global tocando, parar_flag
    while tempo_global_atual() < start_at:
        if parar_flag:
            # Comando STOP chegou antes mesmo da música começar
            parar_flag = False
            tocando = False
            print("Início cancelado por comando STOP.")
            return
        time.sleep_ms(1)

    if len(partitura_atual) > 0:
        reproduzir_musica()
    else:
        tocando = False

# ==========================================
# 6. CONEXÃO WI-FI
# ==========================================
def conectar_wifi() -> None:
    wlan = network.WLAN(network.STA_IF)

    # --- LIMPEZA DE ESTADO DO WI-FI ---
    # Desliga a antena e limpa tentativas de conexão anteriores
    wlan.active(False)
    time.sleep(0.5)

    wlan.active(True)
    wlan.disconnect()  # Garante que está desconectado antes de tentar conectar
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
# 7. LÓGICA DO MQTT (Ouvido do Músico)
# ==========================================
def callback_mensagem(topico: bytes, msg: bytes) -> None:
    """Callback MQTT que processa sincronização, partitura e comandos de controle.

    - `topico` e `msg` são bytes brutos recebidos do cliente MQTT e são decodificados
      para UTF-8 dentro do tratador.
    """
    global partitura_atual, bpm_atual, offset_tempo
    global tocando, parar_flag

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

    # 4. Comandos do maestro: START / STOP / VOLUME_UP / VOLUME_DOWN
    elif topico_str == TOPICO_COMANDO.decode('utf-8'):
        try:
            dados = json.loads(msg_str)
        except ValueError:
            return  # Ignora mensagens fora do padrão JSON

        comando = dados.get("comando")

        if comando == "START":
            start_at = dados.get("start_at")
            print(f"Ordem recebida! A música começará no instante global: {start_at}")
            if tocando:
                print("Já existe uma música em execução, ignorando novo START.")
                return
            tocando = True
            parar_flag = False
            # Roda a espera sincronizada + a reprodução em uma thread própria,
            # para que a thread principal (main loop / check_msg) continue
            # livre para receber STOP e VOLUME_UP/DOWN durante a música.
            _thread.start_new_thread(_executar_reproducao_agendada, (start_at,))

        elif comando == "STOP":
            if tocando:
                parar_flag = True
                print("Comando STOP recebido! Interrompendo a música...")
            else:
                print("Comando STOP recebido, mas nenhuma música está tocando.")

        elif comando == "VOLUME_UP":
            passo = dados.get("passo", VOLUME_PASSO_PADRAO)
            ajustar_volume(passo)

        elif comando == "VOLUME_DOWN":
            passo = dados.get("passo", VOLUME_PASSO_PADRAO)
            ajustar_volume(-passo)

def conectar_mqtt() -> Any:
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
# 8. LOOP PRINCIPAL
# ==========================================
conectar_wifi()
cliente_mqtt = conectar_mqtt()

print("Músico posicionado. Aguardando a partitura e a batuta do maestro...")

tocando_anterior = False

try:
    while True:
        cliente_mqtt.check_msg()  # Ouve o maestro (partitura, START, STOP, VOLUME...)

        # Quando a thread de reprodução termina (tocando: True -> False),
        # aproveita para limpar a memória.
        if tocando_anterior and not tocando:
            gc.collect()
        tocando_anterior = tocando

except KeyboardInterrupt:
    print("\nDesconectando...")
except OSError as e:
    print("Erro de rede. Reconectando...")
finally:
    # Segurança de sempre: pede para a thread de reprodução parar e libera os pinos
    parar_flag = True
    time.sleep_ms(50)
    _desligar_buzzers_ativos()
    cliente_mqtt.disconnect()