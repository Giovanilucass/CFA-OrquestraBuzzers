# CFA-OrquestraBuzzers
- - -
Este repositório possuí as etapas para a criação de uma "orquestra" de buzzers, isto é, um servidor serve de maestro para diversos microcontroladores que, conectados aos buzzers, tocam uma música em diferentes tons ao mesmo tempo.
### Objetivo
O objetivo deste projeto é testar os limites do ESP32 para transmitir diferentes frequências para buzzers de forma paralela, enquanto se conecta a um servidor HTTPS que servirá como maestro. Além de estudar a complexidade das transmissões para garantir sincronismo entre os microocontroladores.
### Materiais
- 1 ESP32
- 3 Buzzers passivos
- 1 Protoboard
- 3 resistores de 220Ohms
### Simulação
A imagem abaixo representa uma simulação do circuito fisíco necessário para um dos ESP32, para que seja possível reproduzir acordes e melodias.

<img width="716" height="662" alt="image" src="https://github.com/user-attachments/assets/059153e9-fd7e-4625-af50-ff5ee9d61856" />

Em seguida montamos o circuito físico baseando-se na simulaçao, porém utilizando resistores de 220Ohms.

<img width="899" height="1599" alt="image" src="https://github.com/user-attachments/assets/f0b7f15b-155c-40f3-a598-efa659a3af75" />
