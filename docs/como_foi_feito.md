# 4. Como o dispositivo foi feito

Descrição dos artefatos e do processo de implementação do nó tocador.

## Componentes de software

- `orquestra/tocador.py`: lógica principal do tocador (conexão Wi‑Fi, MQTT, reprodução).
- `orquestra/umqtt.py`: cliente MQTT compatível com MicroPython.
- `podio/maestro.py`: aplicação desktop/servidor que publica partituras e sincroniza músicos.
- `podio/utils.py`: utilitários para conversão de partituras (`music21`).

## Fluxo de execução

1. Maestro publica `SYNC` e coleta respostas para calcular offset global.
2. Maestro publica partitura(s) e, após sincronização, publica `START` com `start_at`.
3. Tocadores aguardam `start_at` aplicado ao relógio local e reproduzem notas.

## Considerações de implementação

- Uso de PWM para controlar frequência e volume (duty cycle).
- Proteções simples contra travamentos (checagem periódica de `parar_flag`).
- Cuidado com recursos limitados do MicroPython/ESP32 ao manipular listas e threads.

## Conexão física

Fisicamente, o circuito é semelhante ao modelo abaixo — o diagrama mostra como
conectar os buzzers ao ESP32 usando resistores de 220Ω para limitar corrente.

<img width="399" height="1099" alt="diagrama-fisico" src="https://github.com/user-attachments/assets/f0b7f15b-155c-40f3-a598-efa659a3af75" />

Em resumo:

- Conecte cada buzzer passivo a um pino GPIO configurado em `orquestra/tocador.py`.
- Use um resistor de ~220Ω em série com cada buzzer para proteção.
- GND do buzzer deve ser ligado ao GND do ESP32.

Para referência visual da simulação (esquemático usado durante o desenvolvimento),
veja também a imagem de simulação no `README.md`.
