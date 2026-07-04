import music21
import json
import os

# Dicionário de notas permitidas pelo seu sistema
CHAVES_PERMITIDAS = [
    'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
    'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
    'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5'
]

def formatar_nota(pitch):
    """
    Recebe um objeto de tom do music21, converte bemóis para sustenidos
    e ajusta a oitava para se encaixar no dicionário (mínimo C3, máximo B5).
    """
    # Converte a notação do music21 (onde bemol é '-') para 'b'
    nome_nota = pitch.name.replace('-', 'b')
    
    # Dicionário de conversão enarmônica
    enarmonicos = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
    if nome_nota in enarmonicos:
        nome_nota = enarmonicos[nome_nota]
        
    oitava = pitch.octave
    
    # Trava os limites de oitava
    if oitava is None:
        oitava = 4
    elif oitava < 3:
        oitava = 3
    elif oitava > 5:
        oitava = 5
        
    nota_formatada = f"{nome_nota}{oitava}"
    
    # Retorna a nota formatada, ou C3 como fallback de segurança
    return nota_formatada if nota_formatada in CHAVES_PERMITIDAS else 'C3'

def extrair_compassos(part):
    """
    Percorre todos os elementos da pauta em ordem temporal e extrai 
    notas, acordes e pausas no formato [["Nota"], duracao].
    """
    resultado = []
    
    # flat.notesAndRests retira subdivisões de compassos e entrega tudo linearmente
    for elemento in part.flatten().notesAndRests:
        duracao = float(elemento.quarterLength)
        
        # Ignora notas sem duração (grace notes) para não quebrar o tempo
        if duracao == 0:
            continue
            
        if isinstance(elemento, music21.note.Rest):
            resultado.append(["pausa", duracao])
            
        elif isinstance(elemento, music21.note.Note):
            nota_str = formatar_nota(elemento.pitch)
            resultado.append([[nota_str], duracao])
            
        elif isinstance(elemento, music21.chord.Chord):
            # Usamos set() para remover notas duplicadas no mesmo acorde após o ajuste de oitavas
            notas_acorde = list(set([formatar_nota(p) for p in elemento.pitches]))
            resultado.append([notas_acorde, duracao])
            
    return resultado

def converter_mxl_para_json(caminho_mxl, caminho_saida='partitura_convertida.json'):
    print(f"Processando '{caminho_mxl}'...")
    
    if not os.path.exists(caminho_mxl):
        print(f"Erro: Arquivo {caminho_mxl} não encontrado.")
        return

    # O music21 descompacta e lê o arquivo .mxl automaticamente
    partitura = music21.converter.parse(caminho_mxl)
    
    dados_json = {}
    
    # Assumimos que partitura.parts[0] é a Clave de Sol e parts[1] é a Clave de Fá
    if len(partitura.parts) >= 1:
        dados_json["clave_de_sol"] = extrair_compassos(partitura.parts[0])
    
    if len(partitura.parts) >= 2:
        dados_json["clave_de_fa"] = extrair_compassos(partitura.parts[1])
        
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(dados_json, f, indent=2)
        
    print(f"Sucesso! Arquivo salvo como '{caminho_saida}'.")

# Execução do script
if __name__ == "__main__":
    nome_arquivo = './podio/repertorio/Fur_Elise_Easy_Piano.mxl'
    converter_mxl_para_json(nome_arquivo, './podio/repertorio/fur_elise.json')