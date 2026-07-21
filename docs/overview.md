# 1. O que o dispositivo faz

Resumo curto do propósito e do comportamento do dispositivo.

## Objetivo

Este projeto cria uma "orquestra" de buzzers: um maestro (publisher) publica
partituras e comandos via MQTT e vários dispositivos (ESP32) conectados a
buzzers reproduzem as notas sincronizadas.

## Comportamento principal

- Conectar-se ao Wi‑Fi e ao broker MQTT.
- Receber partituras em JSON e comandos (START/STOP/VOLUME).
- Sincronizar o relógio via algoritmo tipo Berkeley.
- Reproduzir notas e acordes em buzzer(s) locais com PWM.

## Público-alvo

Pessoas que querem reproduzir música em paralelo em múltiplos microcontroladores
ou estudar sincronização/controle distribuído em dispositivos embarcados.
