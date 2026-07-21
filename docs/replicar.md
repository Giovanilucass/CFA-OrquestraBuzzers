# 3. Replicar o dispositivo

Instruções para replicar um nó (ESP32 + 3 buzzers) usado no projeto.

## Materiais mínimos (BOM)

- 1x ESP32
- 3x buzzers passivos
- 3x resistores 220Ω
- Jumpers e protoboard

Veja `docs/bom.md` para uma lista detalhada.

## Montagem básica

1. Conectar cada buzzer a um pino PWM do ESP32 via resistor de 220Ω.
2. Conectar os GNDs corretamente.
3. Carregar o firmware MicroPython e os scripts do repositório no ESP32.

## Configuração de software

1. Editar credenciais Wi‑Fi (`WIFI_SSID`, `WIFI_PASSWORD`) em `orquestra/tocador.py`.
2. Ajustar endereço do broker MQTT se necessário.
3. Reinicializar o dispositivo; verificar logs seriais.
