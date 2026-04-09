from machine import Pin, PWM
from time import sleep

# ==========================================
# 1. LIMPEZA DE SEGURANÇA (Garante que os pinos começam livres)
# ==========================================
pinos = [Pin(0, Pin.OUT), Pin(2, Pin.OUT), Pin(5, Pin.OUT)]
for p in pinos:
    try:
        PWM(p).deinit()
    except:
        pass

# Lista global para rastrear os buzzers que estão tocando no exato momento
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
        
    # O PULO DO GATO: Em vez de mudar a frequência, CRIAMOS um PWM novo para cada nota!
    for i in range(len(notas)):
        if i < 3: 
            nota = notas[i]
            if nota in notas_padrao:
                # Aloca o timer apenas na hora de tocar
                buzzer = PWM(pinos[i], freq=notas_padrao[nota], duty=300)
                buzzers_ativos.append(buzzer)

    # Mantém a nota tocando pelo tempo determinado
    sleep(duracao_segundos)

    # DESTRÓI os buzzers ativos. Isso arranca o timer do hardware e devolve pro ESP32!
    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except:
            pass
            
    # Esvazia a lista para o próximo compasso
    buzzers_ativos.clear()
    
    sleep(0.02) 

def reproduzir_musica(partitura, bpm):
    print(f"Iniciando música a {bpm} BPM...")
    for passo in partitura:
        tocar_passo(passo[0], passo[1], bpm)
    print("Música finalizada!")

# ==========================================
# 4. EXECUÇÃO PRINCIPAL
# ==========================================
try:
    while True:
        reproduzir_musica(twice, 140)
        sleep(2) 

except KeyboardInterrupt:
    print("\nVocê apertou Stop. Parando a música...")
except Exception as e:
    print(f"\nErro no código: {e}")
finally:
    # Caso o código seja interrompido no meio da nota, matamos os objetos com segurança
    for b in buzzers_ativos:
        try:
            b.duty(0)
            b.deinit()
        except:
            pass
    print("Pronto! Timers liberados com sucesso. Código limpo.")
