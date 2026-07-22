from machine import Pin, I2C
import ssd1306

class DisplayFeedback:
    def __init__(self, scl_pin=22, sda_pin=21, i2c_freq=400000):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=i2c_freq)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.voz_nome = "VOZ 1 - MELODIA"
        
        # --- ESTADO INTERNO DO DISPLAY ---
        self.cursor_x = 10         # Posição inicial da nota
        self.passo_x = 16          # Distância horizontal entre notas
        self.limite_x = 115        # Limite da tela antes de "virar a página"
        
        # --- DICIONÁRIO VISUAL (Encapsulado no módulo de vídeo) ---
        self.notas_offset = {
            'C3': 64, 'C#3': 64, 'D3': 64, 'D#3': 64,
            'C4': 62, 'C#4': 62, 'D4': 58, 'D#4': 58, 
            'E4': 54, 'F4': 50, 'F#4': 50, 'G4': 46, 'G#4': 46, 
            'A4': 42, 'A#4': 42, 'B4': 38, 
            'C5': 34, 'C#5': 34, 'D5': 30, 'D#5': 30, 
            'E5': 26, 'F5': 22, 'F#5': 22, 
            'G5': 18, 'G#5': 18, 'A5': 14, 'A#5': 14, 
            'B5': 10
        }

        self.reiniciar_tela()

    def reiniciar_tela(self):
        """Limpa a tela, desenha o pentagrama e devolve o cursor para o início."""
        self.oled.fill(0)
        self.oled.text(self.voz_nome, 4, 2)
        self.oled.hline(0, 12, 128, 1) # Linha de separação
        
        # Desenha as 5 linhas do pentagrama
        for i in range(5):
            y_linha = 22 + (i * 8)
            self.oled.hline(0, y_linha, 128, 1)
            
        self.oled.show()
        self.cursor_x = 10 # Reseta o estado horizontal

    def registrar_acorde(self, notas):
        """
        Recebe as notas atuais, desenha na tela e avança o cursor automaticamente.
        Se chegar no final da tela, limpa e recomeça.
        """
        if notas == "pausa":
            # Para pausas, apenas andamos com o cursor em branco para dar ritmo visual
            self._avancar_cursor()
            return
            
        desenhou = False
        for nota in notas:
            if nota in self.notas_offset:
                y = self.notas_offset[nota]
                self.oled.fill_rect(self.cursor_x, y - 2, 6, 5, 1)
                desenhou = True
                
        if desenhou:
            self.oled.show()
            self._avancar_cursor()

    def _avancar_cursor(self):
        """Método privado para lidar com a lógica de paginação."""
        self.cursor_x += self.passo_x
        if self.cursor_x > self.limite_x:
            self.reiniciar_tela()