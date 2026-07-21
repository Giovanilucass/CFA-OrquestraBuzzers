# 2. Como usar o dispositivo

Guia rápido para operar um dispositivo já montado e configurado.

## Pré-requisitos

- Um ESP32 com firmware MicroPython instalado.
- Rede Wi‑Fi disponível com SSID/senha configurados.
- Broker MQTT acessível (ex.: `broker.hivemq.com`).

Nota: por padrão o tocador vem configurado com Wi‑Fi `WIFI_SSID = "lab8"` e `WIFI_PASSWORD = "lab8arduino"` em `orquestra/tocador.py`.

## Passos para uso

1. Alimentar o ESP32 e verificar que ele conecta ao Wi‑Fi.
2. Garantir que o dispositivo esteja inscrito nos tópicos MQTT do projeto.
3. Enviar uma partitura JSON pelo tópico `projeto/orquestra/partitura`.
4. Enviar `{"comando":"START","start_at": <ms_global>}` para iniciar.
5. Usar `VOLUME_UP`/`VOLUME_DOWN` e `STOP` conforme necessário.

## Comandos MQTT esperados

- `TOPICO_PARTITURA`: payload JSON com `bpm`, `partitura` e opcional `destino`.
- `TOPICO_COMANDO`: comandos `START`/`STOP`/`VOLUME_UP`/`VOLUME_DOWN`.

## Observações

- O `start_at` deve ser um timestamp global (ms) calculado pelo maestro.
- O dispositivo aplica ajuste de relógio enviado via `TOPICO_SYNC_ADJ`.
