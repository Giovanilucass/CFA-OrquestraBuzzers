# 5. Como o dispositivo foi projetado

Decisões de design, trade‑offs e arquitetura do sistema.

## Arquitetura

- Topologia: um publisher (maestro) e vários subscribers (tocadores).
- Comunicação: MQTT (broker público ou privado).
- Sincronização: algoritmo inspirado em Berkeley para ajustar relógios.

## Decisões relevantes

- Por que MQTT: leve, distribuído e com suporte amplo em microcontroladores.
- Por que PWM: permite controle de frequência e volume em buzzers passivos.
- Limites: cada nó é simples (até 3 buzzers) para reduzir complexidade e uso de memória.

## Possíveis melhorias

- Implementar jitter compensation e medidas de latência mais sofisticadas.
- Usar TLS/SSL e autenticação para ambientes não confiáveis.
