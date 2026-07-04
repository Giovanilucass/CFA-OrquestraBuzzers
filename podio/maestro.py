import json
import time
from pathlib import Path
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORTA = 1883

TOPICO_PARTITURA = "projeto/orquestra/partitura"
TOPICO_COMANDO = "projeto/orquestra/comando"


class Maestro:
    def __init__(self, broker=BROKER, porta=PORTA, caminho_partituras=None):
        self.broker = broker
        self.porta = porta
        self.caminho_partituras = caminho_partituras or Path(__file__).with_name("partituras.json")
        self.partituras = {}
        self.client = None
        self.conectado = False

    def ler_partituras_do_arquivo(self):
        print(f"Lendo as partituras do arquivo '{self.caminho_partituras}'...")
        try:
            with self.caminho_partituras.open("r", encoding="utf-8") as arquivo:
                self.partituras = json.load(arquivo)
                return self.partituras
        except FileNotFoundError:
            print(f"ERRO: Arquivo '{self.caminho_partituras}' não encontrado.")
            return {}
        except ValueError:
            print("ERRO: O arquivo possui JSON inválido.")
            return {}

    def listar_musicas(self):
        if not self.partituras:
            self.ler_partituras_do_arquivo()
        return sorted(self.partituras.keys())

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.conectado = True
            print(f"Conectado ao broker MQTT ({self.broker}:{self.porta}).")
        else:
            print(f"Falha ao conectar ao broker MQTT. Código: {reason_code}")

    def conectar(self):
        print(f"Conectando ao Broker MQTT ({self.broker}:{self.porta})...")
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except AttributeError:
            self.client = mqtt.Client()
        except TypeError:
            self.client = mqtt.Client()

        self.client.on_connect = self._on_connect
        self.client.connect(self.broker, self.porta, 60)
        self.client.loop_start()

        while not self.conectado:
            time.sleep(0.1)

    def enviar_musica(self, nome_musica, bpm=140):
        if nome_musica not in self.partituras:
            print(f"Música '{nome_musica}' não encontrada.")
            return

        pacote = {
            "bpm": bpm,
            "musica": nome_musica,
            "partitura": self.partituras[nome_musica],
        }

        payload_json = json.dumps(pacote)
        print(f"Enviando '{nome_musica}' no tópico '{TOPICO_PARTITURA}'...")
        self.client.publish(TOPICO_PARTITURA, payload_json)

        time.sleep(0.5)
        print(f"Enviando comando START no tópico '{TOPICO_COMANDO}'! 🎵")
        self.client.publish(TOPICO_COMANDO, "START")

    def executar(self):
        self.ler_partituras_do_arquivo()
        self.conectar()

        print("Maestro online. Escolha uma música ou digite 's' para sair.")
        while True:
            musicas = self.listar_musicas()
            print("\nMúsicas disponíveis:")
            for indice, nome in enumerate(musicas, start=1):
                print(f"  {indice}. {nome}")

            escolha = input("Escolha o número da música: ").strip().lower()
            if escolha in {"s", "q", "quit", "exit"}:
                break

            try:
                indice = int(escolha) - 1
            except ValueError:
                print("Escolha inválida. Digite um número ou 's' para sair.")
                continue

            if 0 <= indice < len(musicas):
                nome_musica = musicas[indice]
                self.enviar_musica(nome_musica)
            else:
                print("Escolha fora da lista.")

        self.encerrar()

    def encerrar(self):
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
        print("Maestro encerrado.")


if __name__ == "__main__":
    maestro = Maestro()
    maestro.executar()