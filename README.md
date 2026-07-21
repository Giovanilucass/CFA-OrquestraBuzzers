# CFA-OrquestraBuzzers
Este repositório possui os componentes para a criação de uma "orquestra" de buzzers, isto é, um publisher serve de maestro para diversos microcontroladores que, conectados aos buzzers, tocam uma música em diferentes tons ao mesmo tempo. Agradecemos profundamente a Steven Swann por disponibilizar uma [implementação de uMQTT para ESP32](https://github.com/sjs205/uMQTT).
## Objetivo
O objetivo deste projeto é testar os limites do ESP32 para transmitir diferentes frequências para buzzers de forma paralela, enquanto se conecta a um servidor HTTPS que servirá como maestro. Além de estudar a complexidade das transmissões para garantir sincronismo entre os microocontroladores.

## Como construir um tocador
A imagem abaixo representa uma simulação do circuito fisíco necessário para um dos ESP32, para que seja possível reproduzir acordes e melodias.

<img width="516" height="462" alt="image" src="https://github.com/user-attachments/assets/059153e9-fd7e-4625-af50-ff5ee9d61856" />

### Materiais
- 1 ESP32
- 3 Buzzers passivos
- 1 Protoboard
- 3 resistores de 220Ohms

## Ferramentas
- Python para o maestro
- MicroPython para o tocador (ESP32)
- Wokwi para construção dos diagramas

Para ver um exemplo real, veja a seção **Como o dispositivo foi feito** em [docs/como_foi_feito.md](docs/como_foi_feito.md).

## Uso rápido

Um resumo curto de como operar um dispositivo: o tocador conecta-se ao Wi‑Fi
e ao broker MQTT, fica inscrito nos tópicos do projeto e aguarda partitura(s)
e comandos do maestro. Veja `docs/usage.md` para instruções detalhadas — por
padrão o Wi‑Fi do tocador está configurado com nome `lab8` e senha `lab8arduino`.

### Como rodar o maestro (PC)

Passos mínimos para executar o maestro localmente (máquina com Python):

1. Crie/ative um ambiente virtual (opcional):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale a dependência MQTT:

```bash
pip install paho-mqtt
```

3. Rode o maestro:

```bash
python -m podio.maestro
```

O maestro irá ler partituras em `podio/repertorio/`, conectar-se ao broker e
permitir enviar músicas para os tocadores.

### Como rodar o tocador (ESP32)

O tocador foi desenvolvido para MicroPython no ESP32. Passos resumidos:

1. Copie a pasta `orquestra/` para o ESP32 usando `mpremote`, `ampy` ou outra
	ferramenta de transferência para MicroPython.

Exemplo com `mpremote` (substitua `/dev/ttyUSB0` pela porta correta):

```bash
mpremote connect /dev/ttyUSB0 fs put -r orquestra /
mpremote connect /dev/ttyUSB0 run /orquestra/main.py
```

2. Alternativamente, conecte ao REPL do dispositivo e importe o módulo:

```python
import orquestra.main
```

Observe que as credenciais Wi‑Fi padrão estão definidas em `orquestra/tocador.py`
(`WIFI_SSID = "lab8"`, `WIFI_PASSWORD = "lab8arduino"`).

## Documentação completa

Esta documentação inicial foi organizada em sete seções, conforme o planejado:

- [1. O que o dispositivo faz](docs/overview.md)
- [2. Como usar o dispositivo](docs/usage.md)
- [3. Replicar o dispositivo](docs/replicar.md)
- [4. Como o dispositivo foi feito](docs/como_foi_feito.md)
- [5. Como o dispositivo foi projetado](docs/projeto.md)
- [6. Como o dispositivo foi documentado](docs/documentacao_dispositivo.md)
- [7. Desenvolvimento e histórico do projeto](docs/desenvolvimento.md)

Outros recursos:

- [BOM (lista de materiais)](docs/bom.md)

## Melhorias futuras

Veja [Melhorias Futuras](docs/melhorias_futuras.md) para itens planejados,
incluindo separar as configurações de Wi‑Fi em arquivo paramétrico, criar
uma fila UMQTT dedicada para clientes e adicionar mais músicas ao repertório.

