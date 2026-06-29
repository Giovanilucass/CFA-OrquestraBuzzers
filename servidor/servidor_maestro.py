import paho.mqtt.client as mqtt
import json
import time

# ==========================================
# 1. CONFIGURAÇÕES DO SERVIDOR MQTT (BROKER)
# ==========================================
# Usando um broker público para testes rápidos. 
# Em produção, você pode rodar o seu próprio (ex: Mosquitto).
BROKER = "broker.hivemq.com"
PORTA = 1883

# Tópicos onde os ESP32 estarão inscritos (escutando)
TOPICO_PARTITURA = "projeto/orquestra/partitura"
TOPICO_COMANDO = "projeto/orquestra/comando"

# ==========================================
# 2. A PARTITURA A SER ENVIADA
# ==========================================
# Pegando a sua partitura do TWICE como exemplo
estrelinha = [
    # ==========================================
    # PARTE 1: TEMA PRINCIPAL
    
    # Compasso 1 (Dó, Dó, Sol, Sol)
    (['C4', 'C3'], 1), (['C4', 'C3'], 1), (['G4', 'E3'], 1), (['G4', 'E3'], 1),
    
    # Compasso 2 (Lá, Lá, Sol) - O Sol dura 2 tempos (nota branca/mínima)
    (['A4', 'F3'], 1), (['A4', 'F3'], 1), (['G4', 'C3'], 2),
    
    # Compasso 3 (Fá, Fá, Mi, Mi)
    (['F4', 'D3'], 1), (['F4', 'D3'], 1), (['E4', 'C3'], 1), (['E4', 'C3'], 1),
    
    # Compasso 4 (Ré, Ré, Dó)
    (['D4', 'G3'], 1), (['D4', 'G3'], 1), (['C4', 'C3'], 2),

    # ==========================================
    # PARTE 2: REFRÃO (A estrelinha brilhando lá no alto)
    
    # Compasso 5 (Sol, Sol, Fá, Fá)
    (['G4', 'E3'], 1), (['G4', 'E3'], 1), (['F4', 'D3'], 1), (['F4', 'D3'], 1),
    
    # Compasso 6 (Mi, Mi, Ré)
    (['E4', 'C3'], 1), (['E4', 'C3'], 1), (['D4', 'G3'], 2),
    
    # Compasso 7 (Repete o Compasso 5)
    (['G4', 'E3'], 1), (['G4', 'E3'], 1), (['F4', 'D3'], 1), (['F4', 'D3'], 1),
    
    # Compasso 8 (Repete o Compasso 6)
    (['E4', 'C3'], 1), (['E4', 'C3'], 1), (['D4', 'G3'], 2),

    # ==========================================
    # PARTE 3: RETORNO AO TEMA (Igual à Parte 1)
    
    # Compasso 9
    (['C4', 'C3'], 1), (['C4', 'C3'], 1), (['G4', 'E3'], 1), (['G4', 'E3'], 1),
    
    # Compasso 10
    (['A4', 'F3'], 1), (['A4', 'F3'], 1), (['G4', 'C3'], 2),
    
    # Compasso 11
    (['F4', 'D3'], 1), (['F4', 'D3'], 1), (['E4', 'C3'], 1), (['E4', 'C3'], 1),
    
    # Compasso 12 (Finalização)
    (['D4', 'G3'], 1), (['D4', 'G3'], 1), (['C4', 'C3'], 2),
    
    ("pausa", 1) # Pausa final
]

tetris = [
    # PARTE A
    # Compasso 1 (Acorde E)
    (['E5', 'E3', 'G#3'], 1), (['B4'], 0.5), (['C5'], 0.5),
    (['D5', 'E3', 'G#3'], 1), (['C5'], 0.5), (['B4'], 0.5),

    # Compasso 2 (Acorde Am)
    (['A4', 'A3', 'C4'], 1), (['A4'], 0.5), (['C5'], 0.5),
    (['E5', 'A3', 'C4'], 1), (['D5'], 0.5), (['C5'], 0.5),

    # Compasso 3 (Acorde E -> Am)
    (['B4', 'E3', 'G#3'], 1), (['B4'], 0.5), (['C5'], 0.5),
    (['D5', 'E3', 'G#3'], 1), (['E5', 'A3', 'C4'], 1),

    # Compasso 4 (Acorde Am - Pausa no final)
    (['C5', 'A3', 'E4'], 1), (['A4', 'A3'], 1), (['A4', 'A3', 'C4'], 1), ("pausa", 1),

    # PARTE B
    # Compasso 5 (Acorde Dm)
    (['D3', 'F3'], 1), (['D5', 'D3', 'F3'], 1), (['F5', 'D3', 'F3'], 0.5),
    (['A5'], 0.5), (['G5', 'D3', 'F3'], 0.5), (['F5'], 0.5),

    # Compasso 6 (Acorde C)
    (['E5', 'C3', 'E3'], 1), (['E5'], 0.5), (['C5'], 0.5),
    (['E5', 'C3', 'E3'], 1), (['D5', 'C3'], 0.5), (['C5'], 0.5),

    # Compasso 7 (Acorde E)
    (['B4', 'E3', 'G#3'], 1), (['B4'], 0.5), (['C5'], 0.5),
    (['D5', 'E3', 'G#3'], 1), (['E5', 'E3'], 1),

    # Compasso 8 (Acorde Am - Finalização da frase)
    (['C5', 'A3', 'C4'], 1), (['A4', 'A3'], 1), (['A4', 'A3', 'C4'], 2)
]

twice = [
    # Compasso 45 (Acorde Mim / Em) - Melodia(B4) + Base(E3, B3)
    (['B4', 'E3', 'B3'], 1), (['G4'], 1), (['E4'], 1), (['B3'], 1),
    
    # Compasso 46 (Melodia apenas)
    (['E4'], 0.5), (['F#4'], 0.5), (['G4'], 1), (['A4'], 0.5), (['G4'], 0.5), (['F#4'], 1),
    
    # Compasso 47 (Acorde Dom / Cm) - Melodia(C5) + Base(C3, G3)
    (['C5', 'C3', 'G3'], 1), (['G4'], 1), (['D#4'], 1), (['C4'], 1),
    
    # Compasso 48
    (['D4'], 0.5), (['D#4'], 0.5), (['F4'], 1), (['G4'], 0.5), (['F4'], 0.5), (['D#4'], 1),
    
    # Compasso 49 (Acorde Sol / G) - Melodia(G4) + Base(G3, D4)
    (['G4', 'G3', 'D4'], 1), (['D4'], 1), (['B3'], 1), (['G3'], 1),
    
    # Compasso 50
    (['A3'], 0.5), (['B3'], 0.5), (['C4'], 1), (['D4'], 0.5), (['C4'], 0.5), (['B3'], 1),
    
    # Compasso 51 (Acorde Sim / Bm) - Melodia(F#4) + Base(B3, F#3)
    (['F#4', 'B3', 'F#3'], 1), (['D4'], 1), (['B3'], 1), (['F#3'], 1),
    
    # Compasso 52
    (['G3'], 0.5), (['A3'], 0.5), (['B3'], 1), (['C4'], 0.5), (['B3'], 0.5), (['A3'], 1),
    
    # Compasso 53 (Acorde Mim / Em) - Melodia(G4) + Base(E3, B3)
    (['G4', 'E3', 'B3'], 1), (['E4'], 1), (['B3'], 1), (['E3'], 1),
    
    # Compasso 54
    (['F#3'], 0.5), (['G3'], 0.5), (['A3'], 1), (['B3'], 0.5), (['A3'], 0.5), (['G3'], 1),
    
    # Compasso 55 (Acorde Dom / Cm) - Melodia(C5) + Base(C3, G3)
    (['C5', 'C3', 'G3'], 1), (['G4'], 1), (['D#4'], 1), (['C4'], 1),
    
    # Compasso 56
    (['D4'], 0.5), (['D#4'], 0.5), (['F4'], 1), (['G4'], 0.5), (['F4'], 0.5), (['D#4'], 1),
    
    # Compasso 57 (Acorde Sol / G final) - Nota longa de 4 tempos para finalizar
    (['G4', 'G3', 'D4'], 4)
]

death_by_glamour = [
    # ==========================================
    # INTRODUÇÃO - A LINHA DE BAIXO CLÁSSICA (Compassos 1 e 2)
    # Tocado em oitavas (E3 e E4) para dar um efeito de "sintetizador pesado"
    
    ("pausa", 0.5), (['E4', 'E3'], 0.5), (['E4', 'E3'], 0.5), (['G4', 'G3'], 0.5),
    (['E4', 'E3'], 0.5), (['D4', 'D3'], 0.5), (['D#4', 'D#3'], 0.5), (['B3'], 0.5),

    ("pausa", 0.5), (['E4', 'E3'], 0.5), (['E4', 'E3'], 0.5), (['G4', 'G3'], 0.5),
    (['E4', 'E3'], 0.5), (['D4', 'D3'], 0.5), (['D#4', 'D#3'], 0.5), (['B3'], 0.5),

    # ==========================================
    # MELODIA PRINCIPAL (A partir do Compasso 9 da imagem)
    # Buzzer 1 faz a voz, Buzzers 2 e 3 fazem a marcação de tempo e acordes
    
    # Compasso 9 (Acorde Base: Mi Menor - Em)
    (['B4', 'E3', 'B3'], 1),
    (['D5', 'G3', 'B3'], 1),
    (['B4', 'E3', 'B3'], 2),

    # Compasso 10 (Acorde Base: Dó Maior - C)
    # O 'B4' se estende (ligadura), enquanto o baixo muda
    (['B4', 'C3', 'G3'], 2), 
    (['A4', 'C3', 'E3'], 1),
    (['G4', 'C3', 'E3'], 1),

    # Compasso 11 (Acorde Base: Lá Menor - Am)
    (['A4', 'A3', 'E4'], 2),
    (['B4', 'A3', 'C4'], 1),
    (['E4', 'A3', 'C4'], 1),

    # Compasso 12 (Resolução: Retorna para Mi Menor - Em)
    (['E4', 'E3', 'B3'], 3),
    ("pausa", 1)
]

funk = [
    # ==========================================
    # INTRODUÇÃO (Os 3 buzzers imitam a batida do violão)
    # Compasso 1: Acorde de Bm (Si Menor)
    (['F#4', 'D4', 'B3'], 0.75), ("pausa", 0.25),
    (['F#4', 'D4', 'B3'], 0.5), (['F#4', 'D4', 'B3'], 0.5),
    ("pausa", 0.5), (['F#4', 'D4', 'B3'], 0.5),
    (['F#4', 'D4', 'B3'], 1),

    # Compasso 2: Acorde de F#m (Fá Sustenido Menor)
    (['F#4', 'C#4', 'F#3'], 0.75), ("pausa", 0.25),
    (['F#4', 'C#4', 'F#3'], 0.5), (['F#4', 'C#4', 'F#3'], 0.5),
    ("pausa", 0.5), (['F#4', 'C#4', 'F#3'], 0.5),
    (['F#4', 'C#4', 'F#3'], 1),
    
    # (Para não ficar enorme, vamos pular direto para a entrada do Violino)

    # ==========================================
    # MELODIA (Buzzer 1 faz Violino, Buzzers 2 e 3 fazem Violão)
    # Compasso 5: Violino entra no meio do compasso
    (['F#4', 'D4', 'B3'], 2), # Violão toca e segura
    (['D5', 'D4', 'B3'], 1), (['C#5', 'D4', 'B3'], 1), # Violino toca D5 e C#5

    # Compasso 6
    (['B4', 'C#4', 'F#3'], 1), (['A4'], 0.5), (['B4'], 0.5), # Violino ágil
    (['F#4', 'C#4', 'F#3'], 2), # Base segura

    # Compasso 7: Acorde de G (Sol Maior)
    (['G4', 'B3', 'G3'], 1), (['F#4'], 0.5), (['G4'], 0.5),
    (['E4', 'B3', 'G3'], 2),

    # Compasso 8: Preparação para o "Drop"
    (['D4', 'A3', 'F#3'], 0.5), (['E4'], 0.5), (['F#4', 'A3', 'F#3'], 1),
    (['F#4', 'C#4', 'A#3'], 2) # Acorde de F# Maior (traz tensão para voltar ao início)
]

fortuna = [
    # ==========================================
    # PARTE 1: PESANTE (Lento, Forte e Pesado)
    # Acordes massivos (Power Chords) para dar peso ao som.
    
    # "O..." (Acorde Dm gigante - 6 tempos de duração)
    (['D4', 'A3', 'D3'], 6),

    # "For - tu - na..."
    (['D4', 'A3', 'D3'], 2), (['D4', 'A3', 'D3'], 2), (['C4', 'G3', 'C3'], 2),

    # "ve - lut  Lu - na..."
    (['C4', 'G3', 'C3'], 2), (['C4', 'G3', 'C3'], 2), (['D4', 'A3', 'D3'], 2),
    
    # "sta - tu  va - ri..." 
    (['D4', 'A3', 'D3'], 2), 
    ("pausa", 2), # Pausa dramática que tem na partitura antes da explosão

    # ==========================================
    # PARTE 2: STRINGENDO (Rápido, Feroz e Pulsante)
    # "semper crescis aut decrescis..."
    # Aqui os tempos caem para 0.5, criando um pulso acelerado.
    
    # Compasso rápido 1 (Melodia subindo)
    (['D4', 'F4', 'D3'], 0.5), (['D4', 'F4', 'D3'], 0.5), # Dm
    (['D4', 'F4', 'D3'], 0.5), (['D4', 'F4', 'D3'], 0.5), # Dm
    (['E4', 'G4', 'C3'], 0.5), (['E4', 'G4', 'C3'], 0.5), # C
    (['F4', 'A4', 'D3'], 0.5), (['F4', 'A4', 'D3'], 0.5), # F

    # Compasso rápido 2 (Melodia descendo)
    (['F4', 'A4', 'D3'], 0.5), (['F4', 'A4', 'D3'], 0.5), # F
    (['E4', 'G4', 'C3'], 0.5), (['D4', 'F4', 'D3'], 0.5), # C -> Dm
    (['C4', 'E4', 'C3'], 0.5), (['D4', 'F4', 'D3'], 0.5), # C -> Dm
    (['D4', 'F4', 'D3'], 1), ("pausa", 1),                # Dm finaliza a frase
    
    # Repete o padrão frenético (opcional para dar mais corpo à execução)
    (['D4', 'F4', 'D3'], 0.5), (['D4', 'F4', 'D3'], 0.5),
    (['D4', 'F4', 'D3'], 0.5), (['D4', 'F4', 'D3'], 0.5),
    (['E4', 'G4', 'C3'], 0.5), (['E4', 'G4', 'C3'], 0.5),
    (['F4', 'A4', 'D3'], 0.5), (['F4', 'A4', 'D3'], 0.5),
    
    (['F4', 'A4', 'D3'], 0.5), (['F4', 'A4', 'D3'], 0.5),
    (['E4', 'G4', 'C3'], 0.5), (['D4', 'F4', 'D3'], 0.5),
    (['C4', 'E4', 'C3'], 0.5), (['D4', 'F4', 'D3'], 0.5),
    (['D4', 'A3', 'D3'], 4) # Encerra com um acorde longo e grave
]

fireworks = [
    # ==========================================
    # PARTE 1: TEMA PRINCIPAL (2 Vozes)
    
    # Compasso 1 (Acorde Em)
    (['E3'], 0.5), (['E3', 'E5'], 0.5), (['B3', 'G5'], 0.5), (['B3', 'F#5'], 0.5),
    (['G3', 'E5'], 1), (['B3', 'B4'], 1),

    # Compasso 2 (Acorde Em)
    (['E3'], 0.5), (['E3', 'E5'], 0.5), (['B3', 'G5'], 0.5), (['B3', 'F#5'], 0.5),
    (['G3', 'E5'], 1), (['B3', 'B4'], 1),

    # Compasso 3 (Acorde C)
    (['C3'], 0.5), (['C3', 'E5'], 0.5), (['G3', 'G5'], 0.5), (['G3', 'F#5'], 0.5),
    (['E3', 'E5'], 1), (['G3', 'B4'], 1),

    # Compasso 4 (Acorde C)
    (['C3'], 0.5), (['C3', 'E5'], 0.5), (['G3', 'G5'], 0.5), (['G3', 'F#5'], 0.5),
    (['E3', 'E5'], 1), (['G3', 'B4'], 1),

    # Compasso 5 (Acorde D)
    (['D3'], 0.5), (['D3', 'E5'], 0.5), (['A3', 'G5'], 0.5), (['A3', 'F#5'], 0.5),
    (['F#3', 'E5'], 1), (['A3', 'B4'], 1),

    # Compasso 6 (Acorde D - Melodia desce)
    (['D3'], 0.5), (['D3', 'E5'], 0.5), (['A3', 'G5'], 0.5), (['A3', 'F#5'], 0.5),
    (['F#3', 'D5'], 1), (['A3', 'A4'], 1),

    # Compasso 7 (Acorde Em - Retorno ao tema)
    (['E3'], 0.5), (['E3', 'E5'], 0.5), (['B3', 'G5'], 0.5), (['B3', 'F#5'], 0.5),
    (['G3', 'E5'], 1), (['B3', 'B4'], 1),

    # Compasso 8 (Acorde Em - Frase rápida de oitavas)
    (['E3'], 0.5), (['E3', 'E5'], 0.5), (['B3', 'G5'], 0.5), (['B3', 'F#5'], 0.5),
    (['G3', 'E5'], 0.5), (['G3', 'B5'], 0.5), (['B3', 'G5'], 0.5), (['B3', 'E5'], 0.5),

    # ==========================================
    # PARTE 2: EXPLOSÃO (3 Vozes - Todos os buzzers tocando!)
    
    # Compasso 9 (Acorde Em cheio)
    (['E3'], 0.5), (['E3', 'E5', 'G5'], 0.5), (['B3', 'G5', 'B5'], 0.5), (['B3', 'F#5', 'A5'], 0.5),
    (['G3', 'E5', 'G5'], 1), (['B3', 'B4', 'E5'], 1),

    # Compasso 10 (Acorde Em cheio)
    (['E3'], 0.5), (['E3', 'E5', 'G5'], 0.5), (['B3', 'G5', 'B5'], 0.5), (['B3', 'F#5', 'A5'], 0.5),
    (['G3', 'E5', 'G5'], 1), (['B3', 'B4', 'E5'], 1),

    # Compasso 11 (Acorde C cheio)
    (['C3'], 0.5), (['C3', 'E5', 'G5'], 0.5), (['G3', 'G5', 'B5'], 0.5), (['G3', 'F#5', 'A5'], 0.5),
    (['E3', 'E5', 'G5'], 1), (['G3', 'C5', 'E5'], 1),

    # Compasso 12 (Acorde C cheio)
    (['C3'], 0.5), (['C3', 'E5', 'G5'], 0.5), (['G3', 'G5', 'B5'], 0.5), (['G3', 'F#5', 'A5'], 0.5),
    (['E3', 'E5', 'G5'], 1), (['G3', 'C5', 'E5'], 1),
    
    # Pausa final dramática para não cortar o som seco
    ("pausa", 2)
]

chopin = [
    # ==========================================
    # TEMA MAJESTOSO (Abertura da Orquestra)
    
    # Compasso 1 (Acorde de Fá Menor ditando o ritmo)
    (['F3', 'G#3', 'C4'], 1), (['F3', 'G#3', 'C4'], 1), 
    (['C4', 'G#3', 'C4'], 1), (['F4', 'G#3', 'C4'], 1),

    # Compasso 2 (A melodia chora e desce)
    (['G4', 'E3', 'A#3'], 1.5), (['G#4'], 0.5), 
    (['G4', 'E3', 'A#3'], 1), (['F4', 'F3', 'G#3'], 1),

    # Compasso 3 (Tensão)
    (['C4', 'C3', 'G3'], 2), 
    (['C#4', 'A#3', 'F3'], 1.5), (['A#3'], 0.5),

    # Compasso 4 (Respiro dramático no acorde de Láb Maior)
    (['C4', 'G#3', 'D#3'], 4),

    # Compasso 5 (A melodia volta com mais força)
    (['F4', 'F3', 'G#3'], 1.5), (['G4'], 0.5), 
    (['G#4', 'F3', 'G#3'], 1), (['F4', 'F3', 'G#3'], 1),

    # Compasso 6 (Subida heróica)
    (['C5', 'G#3', 'D#4'], 2), 
    (['A#4', 'C#4', 'G4'], 2),

    # Compasso 7 (Preparação para o fim da frase)
    (['G#4', 'C4', 'F4'], 1.5), (['F4'], 0.5), 
    (['G4', 'A#3', 'E4'], 1.5), (['E4'], 0.5),

    # Compasso 8 (Resolução de volta para Fá Menor - Acorde longo)
    (['F4', 'F3', 'C4'], 3), ("pausa", 1)
]

# Construindo o pacote (Payload) para envio
pacote = {
    "bpm": 140,
    "musica": "Tetris",
    "partitura": tetris
}

# ==========================================
# 3. LÓGICA DE PUBLICAÇÃO
# ==========================================
def iniciar_servidor():
    print(f"Conectando ao Broker MQTT ({BROKER})...")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORTA, 60)
    
    # 1º Passo: Converte o pacote Python para formato JSON (texto universal)
    payload_json = json.dumps(pacote)
    
    # 2º Passo: Publica a partitura para os ESP32 baixarem
    print(f"Enviando partitura no tópico '{TOPICO_PARTITURA}'...")
    client.publish(TOPICO_PARTITURA, payload_json)
    
    # Dá 3 segundos para garantir que todos os ESP32 do mundo receberam e processaram
    print("Aguardando ESP32 se prepararem...")
    time.sleep(3)
    
    # 3º Passo: Publica o comando de sincronia (Maestro baixando a batuta)
    print(f"Enviando comando START no tópico '{TOPICO_COMANDO}'! 🎵")
    client.publish(TOPICO_COMANDO, "START")
    
    client.disconnect()
    print("Missão cumprida. Servidor encerrado.")

if __name__ == "__main__":
    iniciar_servidor()