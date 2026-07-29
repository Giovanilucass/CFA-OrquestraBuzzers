from micropython import const
import framebuf

# Registradores do SH1106
_SET_CONTRAST        = const(0x81)
_SET_NORM_INV        = const(0xa6)
_SET_DISP            = const(0xae)
_SET_SCAN_DIR        = const(0xc0)
_SET_SEG_REMAP       = const(0xa0)
_LOW_COLUMN_ADDRESS  = const(0x00)
_HIGH_COLUMN_ADDRESS = const(0x10)
_SET_PAGE_ADDRESS    = const(0xB0)

class SH1106:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.poweron()
        self.init_display()

    def init_display(self):
        for cmd in (
            _SET_DISP | 0x00,  # Desliga a tela
            0xd5, 0x80,
            0xa8, self.height - 1,
            0xd3, 0x00,
            0x40,
            0x8d, 0x14 if self.external_vcc else 0x14,
            0x20, 0x00,
            _SET_SEG_REMAP | 0x01,  
            _SET_SCAN_DIR | 0x08,   
            0xda, 0x12,
            _SET_CONTRAST, 0xcf,
            0xd9, 0xf1,
            0xdb, 0x40,
            _SET_NORM_INV | 0x00,
            _SET_DISP | 0x01): # Liga a tela
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(_SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(_SET_DISP | 0x01)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(_SET_PAGE_ADDRESS | page)
            # O SH1106 precisa de um offset de 2 pixels de coluna por padrão do hardware
            self.write_cmd(_LOW_COLUMN_ADDRESS | 2) 
            self.write_cmd(_HIGH_COLUMN_ADDRESS | 0)
            self.write_data(self.buffer[self.width * page : self.width * page + self.width])

    def fill(self, col):
        self.framebuf.fill(col)
        
    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)
        
    def hline(self, x, y, w, col=1):
        self.framebuf.hline(x, y, w, col)
        
    def vline(self, x, y, h, col=1):
        self.framebuf.vline(x, y, h, col)
        
    def fill_rect(self, x, y, w, h, col=1):
        self.framebuf.fill_rect(x, y, w, h, col)

class SH1106_I2C(SH1106):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        write_buf = bytearray(1)
        write_buf[0] = 0x40 # Co=0, D/C#=1 (Data)
        write_buf.extend(buf)
        self.i2c.writeto(self.addr, write_buf)