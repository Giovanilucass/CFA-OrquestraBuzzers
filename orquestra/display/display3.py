from machine import Pin, I2C
import sh1106

class DisplayFeedback:
    def __init__(self, scl_pin=6, sda_pin=5, i2c_freq=400000):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=i2c_freq)
        self.oled = sh1106.SH1106_I2C(128, 64, self.i2c)
        
        # ====================================================
        # ⚙️ CONFIGURAÇÃO INDIVIDUAL DESTE ESP32
        # ====================================================
        self.voz_nome = "VOZ 3"
        self.off_x = 28
        self.off_y = 12
        # ====================================================
        
        # --- ESTADO INTERNO DO DISPLAY ---
        self.cursor_x = 2          
        self.passo_x = 10          
        self.limite_x = 62         
        
        self.notas_offset = {
            # OITAVA 3 (Graves dobrados para o meio)
            'C3': 38, 'C#3': 38, 'D3': 34, 'D#3': 34, 'E3': 30, 
            'F3': 26, 'F#3': 26, 'G3': 22, 'G#3': 22, 'A3': 18, 
            'A#3': 18, 'B3': 14,
            
            # OITAVA 4 (Oitava visual padrão)
            'C4': 38, 'C#4': 38, 'D4': 34, 'D#4': 34, 'E4': 30, 
            'F4': 26, 'F#4': 26, 'G4': 22, 'G#4': 22, 'A4': 18, 
            'A#4': 18, 'B4': 14,
            
            # OITAVA 5 (Agudos dobrados para o meio)
            'C5': 38, 'C#5': 38, 'D5': 34, 'D#5': 34, 'E5': 30, 
            'F5': 26, 'F#5': 26, 'G5': 22, 'G#5': 22, 'A5': 18, 
            'A#5': 18, 'B5': 14
        }

        self.reiniciar_tela()

    def reiniciar_tela(self):
        """Limpa a tela e desenha a interface base."""
        self.oled.fill(0)
        
        # Desenha o nome da voz (ex: VOZ 1)
        self.oled.text(self.voz_nome, 0 + self.off_x, 0 + self.off_y, 1)
        
        # Desenha o Pentagrama
        for i in range(5):
            y_linha = 11 + (i * 6)
            self.oled.hline(0 + self.off_x, y_linha + self.off_y, 72, 1)
            
        self.oled.show()
        self.cursor_x = 2 

    def registrar_acorde(self, notas):
        """Desenha a bolinha da nota e escreve o texto dela na tela."""
        
        if self.cursor_x > self.limite_x:
            self.reiniciar_tela()
            
        if notas == "pausa":
            self._avancar_cursor()
            return
            
        desenhou = False
        
        # --- Lógica Visual: Escrevendo a nota tocada ---
        # Apaga o cantinho superior direito para não sobrepor o texto antigo
        self.oled.fill_rect(self.off_x + 45, self.off_y, 27, 8, 0)
        
        # Transforma a lista em texto (ex: pega ['C4'] e vira "C4")
        texto_notas = "".join(notas)[:3] 
        self.oled.text(texto_notas, self.off_x + 45, self.off_y, 1)

        # Carimba as bolinhas no pentagrama
        for nota in notas:
            if nota in self.notas_offset:
                y = self.notas_offset[nota]
                self.oled.fill_rect(self.cursor_x + self.off_x, y - 2 + self.off_y, 4, 4, 1)
                desenhou = True
                
        if desenhou:
            self.oled.show()
            self._avancar_cursor()

    def _avancar_cursor(self):
        self.cursor_x += self.passo_x